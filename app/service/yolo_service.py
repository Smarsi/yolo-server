import os
import cv2
import threading
import numpy as np
from time import sleep

class Yolo_Service:

    instances_quantity: int
    model: str
    classes_file: str
    classes: list

    # Instances Threads
    threads: list

    # Inference FIFOs
    entry_fifo: list
    output_fifo: list

    # Controller
    running: bool

    def __init__(self, instances_quantity: int, model: str, classes: str):
        self.instances_quantity = instances_quantity
        self.model = model
        self.classes_file = classes
        self.entry_fifo = []
        self.output_fifo = []
        self.threads = []

        self.running = False

    def start_service(self) -> None:
        self.running = True

        # Load Classes File
        with open(self.classes_file, "r") as file:
            self.classes = [line.strip() for line in file.readlines()]

        while len(self.threads) < self.instances_quantity:
            net = cv2.dnn.readNetFromONNX(self.model)
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            thread = threading.Thread(target=self.run, args=(net, ))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def stop_service(self) -> None:
        self.running = False
        for thread in self.threads:
            thread.join()
            self.threads.remove(thread)

    def run(self, network: cv2.dnn.Net):
        while(self.running):
            sleep(0.1)
            data = {}
            confidence_threshold = 0.5
            nms_threshold = 0.4
            if len(self.entry_fifo) > 0:
                data = self.entry_fifo.pop(0)
                id = data["id"]
                img_path = data["img_path"]

                frame = cv2.imread(img_path)
                blob = cv2.dnn.blobFromImage(frame, 1/255, (640, 640), swapRB=True, crop=False)
                network.setInput(blob)
                outputs = network.forward()

                result = []
                boxes = []
                confidences = []
                class_ids = []

                for i in range(outputs.shape[2]):
                    detection = outputs[0, :, i]
                    if np.max(detection[4:]) > 0.5:
                        x_center = detection[0] 
                        y_center = detection[1] 
                        width = detection[2] 
                        height = detection[3]
                        
                        class_id = np.argmax(detection[4:])
                        confidence = np.max(detection[4:])
                        class_name = self.classes[class_id]

                        boxes.append([x_center, y_center, width, height])
                        confidences.append(confidence)    
                        class_ids.append(class_id)

                indices = cv2.dnn.NMSBoxesBatched(boxes, confidences, class_ids, confidence_threshold, nms_threshold)

                if len(indices) > 0:
                    for i in indices.flatten():
                        # ---- Calc BoundingBox Coordinates min & max ----
                        x_center, y_center, width, height = boxes[i]
                        x_min = (x_center - width/2)
                        y_min = (y_center - height/2) 
                        x_max = (x_min + width)
                        y_max = (y_min + height)
                        # -------------------------------------------------

                        # ---- Normalize BoundingBox Coordinates ----------
                        x_center = x_center / 640
                        y_center = y_center / 640
                        width = width / 640
                        height = height / 640
                        x_min = x_min / 640
                        y_min = y_min / 640
                        x_max = x_max / 640
                        y_max = y_max / 640
                        confidence = confidences[i]
                        class_id = class_ids[i]
                        # -------------------------------------------------

                        result.append({
                            "class_id": int(class_id),
                            "class_name": class_name,
                            "confidence": float(confidence),
                            "bb_x_center": float(x_center),
                            "bb_y_center": float(y_center),
                            "bb_width": float(width),
                            "bb_height": float(height),
                            "bb_x_min": float(x_min),
                            "bb_y_min": float(y_min),
                            "bb_x_max": float(x_max),
                            "bb_y_max": float(y_max)
                        })
                                        

                # result.append({
                #     "class_id": int(class_id),
                #     "class_name": class_name,
                #     "confidence": float(class_confidence),
                #     "x_center": float(x_center),
                #     "y_center": float(y_center),
                #     "width": float(width),
                #     "height": float(height)
                # })

                        # print(f"Caixa Delimitadora: ({x_min}, {y_min}, {x_max}, {y_max}), Confiança: {confidence}, Classe: {class_id}, Confiança da Classe: {class_confidence}")

                self.output_fifo.append({"id": id, "output": result})

    def add_frame(self, id: int, img_path: str):
        self.entry_fifo.append({"id": id, "img_path": img_path})
        return
    
    def get_result(self, id: int) -> dict:
        result = None
        while not result:
            for output in self.output_fifo:
                if output["id"] == id:
                    result = output
                    self.output_fifo.remove(output)
                    return result
