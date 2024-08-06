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
            self.classes = file.read().strip().split("\n")

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
            if len(self.entry_fifo) > 0:
                data = self.entry_fifo.pop(0)
                id = data["id"]
                img_path = data["img_path"]

                frame = cv2.imread(img_path)
                blob = cv2.dnn.blobFromImage(frame, 1/255, (640, 640), swapRB=True, crop=False)
                network.setInput(blob)
                output = network.forward()

                result = []
                for i in range(output.shape[2]):
                    detection = output[0, :, i]
                    if detection[4] > 0.5:
                        x_center = detection[0] / 640
                        y_center = detection[1] / 640
                        width = detection[2] / 640
                        height = detection[3] / 640
                        confidence = detection[4]
                        class_scores = detection[5:]

                        # Identificar a classe com maior pontuação
                        class_id = np.argmax(class_scores)
                        class_confidence = class_scores[class_id]
                        class_name = self.classes[class_id]

                        result.append({
                            "class_name": class_name,
                            "confidence": confidence,
                            "class_confidence": class_confidence,
                            "x_center": x_center,
                            "y_center": y_center,
                            "width": width,
                            "height": height
                        })

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
