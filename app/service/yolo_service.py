import os
import cv2
import queue
import threading
import numpy as np
from time import sleep
from datetime import datetime, time

# Logs Import
from .yolo_logger import yolo_log_builder, log_writer, create_traceback_error_log

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

    # Logger File
    log_file: str

    def __init__(self, instances_quantity: int, model: str, classes: str):
        self.log_file = yolo_log_builder()
        self.instances_quantity = instances_quantity
        self.model = model
        self.classes_file = classes
        self.output_fifo = queue.Queue()
        self.threads = []
        self.threads_fifos = []

        self.running = False
        log_writer(self.log_file, f"Service - YOLO Service started successfully. (Called from __init__)")

    def start_service(self) -> None:
        log_writer(self.log_file, f"Service - Starting YOLO Service.")
        self.running = True

        # Load Classes File
        with open(self.classes_file, "r") as file:
            self.classes = [line.strip() for line in file.readlines()]

        for _ in range(self.instances_quantity):
            log_writer(self.log_file, f"Service - Starting YOLO Service Thread. Threads: {len(self.threads)}")
            net = cv2.dnn.readNetFromONNX(self.model)
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

            self.threads_fifos.append([])
            list_idx = len(self.threads_fifos) - 1
            thread = threading.Thread(target=self.run, args=(net, list_idx))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def stop_service(self) -> None:
        self.running = False
        for thread in self.threads:
            thread.join()
            self.threads.remove(thread)

    def run(self, network: cv2.dnn.Net, list_idx: int):
        log_writer(self.log_file, f"Service - YOLO Service started successfully. (Called from run)")
        while(self.running):
            try:
                fifo = self.threads_fifos[list_idx]
                # log_writer(self.log_file, f"Current Entry Fifo Size: {fifo.qsize()}")
                log_writer(self.log_file, f"Service - Current Entry Fifo Size: {len(fifo)}")
                if len(fifo) > 0:
                    # data = fifo.get(timeout=1)
                    data = fifo.pop(0)
                    img = data["img"]
                    id = data["id"]
                    confidence_threshold = 0.5
                    nms_threshold = 0.4
                    blob = cv2.dnn.blobFromImage(img, 1/255, (640, 640), swapRB=True, crop=False)
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
                            y_bottom_center = (y_center + (height/2))
                            y_top_center = (y_center - (height/2))
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
                            y_bottom_center = y_bottom_center / 640
                            y_top_center = y_top_center / 640
                            confidence = confidences[i]
                            class_id = class_ids[i]
                            class_name = self.classes[class_id]
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
                                "bb_y_max": float(y_max),
                                "bb_x_bottom_center": float(x_center),
                                "bb_y_bottom_center": float(y_bottom_center),
                                "bb_x_top_center": float(x_center),
                                "bb_y_top_center": float(y_top_center)
                            })
                    # self.output_fifo.append({"id": id, "output": result, "ready": True})
                    self.output_fifo.put({"id": id, "output": result, "ready": True})
                # except queue.Empty:
                #     log_writer(self.log_file, f"Service - Empty Queue.")
                #     continue
            except Exception as e:
                # self.output_fifo.append({"id": id, "output": [], "ready": False})
                self.output_fifo.put({"id": id, "output": [], "ready": False})
                log_writer(self.log_file, f"Service - Error: {e}")
                continue

    def add_frame(self, id: str, img: np.ndarray):
        min_index = min(range(len(self.threads_fifos)), key=lambda i: len(self.threads_fifos[i]))
        self.threads_fifos[min_index].append({"id": id, "img": img})

        # min_queue = min(self.threads_fifos, key=lambda q: q.qsize())
        # min_queue.put({"id": id, "img": img})
        return
    
    def convert_bytes_to_image(self, img_bytes: bytes):
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    
    def get_result(self, id: int) -> dict:
        # while True:
        #     for i in range(len(self.output_fifo)):
        #         if self.output_fifo[i]["id"] == id:
        #             return self.output_fifo.pop(i)               

        while True:
            try:
                # Tenta obter um item da fila de saída
                result = self.output_fifo.get(timeout=1)
                if result["id"] == id:
                    return result
                else:
                    # Se o resultado não corresponder ao ID desejado, devolve para a fila
                    self.output_fifo.put(result)
            except queue.Empty:
                continue 


## FOR FUTURE ANALYSIS  === COULD WORK WITH A MOST POWERFUL GPU & FRONT CONTROLLERS ===
# class newYolo_Service:

#     def __init__(self, model_path: str, classes_path: str):
#         self.model_path = model_path
#         self.net = None
#         self._load_model()
#         with open(classes_path, "r") as file:
#             self.classes = [line.strip() for line in file.readlines()]

#     def _load_model(self):
#         self.net = cv2.dnn.readNetFromONNX(self.model_path)
#         self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#         self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

#     def get_model(self):
#         return self.net
    
#     def perform_inference(self, image: np.ndarray):
#         result = []
#         blob = cv2.dnn.blobFromImage(image, 1/255, (640, 640), swapRB=True, crop=False)
#         self.net.setInput(blob)
#         outputs = self.net.forward()
        
#         result = []
#         boxes = []
#         confidences = []
#         class_ids = []
#         confidence_threshold = 0.5
#         nms_threshold = 0.4

#         for i in range(outputs.shape[2]):
#             detection = outputs[0, :, i]
#             if np.max(detection[4:]) > 0.5:
#                 x_center = detection[0] 
#                 y_center = detection[1] 
#                 width = detection[2] 
#                 height = detection[3]
                
#                 class_id = np.argmax(detection[4:])
#                 confidence = np.max(detection[4:])
#                 class_name = self.classes[class_id]

#                 boxes.append([x_center, y_center, width, height])
#                 confidences.append(confidence)    
#                 class_ids.append(class_id)

#         indices = cv2.dnn.NMSBoxesBatched(boxes, confidences, class_ids, confidence_threshold, nms_threshold)

#         if len(indices) > 0:
#             for i in indices.flatten():
#                 # ---- Calc BoundingBox Coordinates min & max ----
#                 x_center, y_center, width, height = boxes[i]
#                 x_min = (x_center - width/2)
#                 y_min = (y_center - height/2) 
#                 x_max = (x_min + width)
#                 y_max = (y_min + height)
#                 y_bottom_center = (y_center + (height/2))
#                 y_top_center = (y_center - (height/2))
#                 # -------------------------------------------------

#                 # ---- Normalize BoundingBox Coordinates ----------
#                 x_center = x_center / 640
#                 y_center = y_center / 640
#                 width = width / 640
#                 height = height / 640
#                 x_min = x_min / 640
#                 y_min = y_min / 640
#                 x_max = x_max / 640
#                 y_max = y_max / 640
#                 y_bottom_center = y_bottom_center / 640
#                 y_top_center = y_top_center / 640
#                 confidence = confidences[i]
#                 class_id = class_ids[i]
#                 class_name = self.classes[class_id]
#                 # -------------------------------------------------

#                 result.append({
#                     "class_id": int(class_id),
#                     "class_name": class_name,
#                     "confidence": float(confidence),
#                     "bb_x_center": float(x_center),
#                     "bb_y_center": float(y_center),
#                     "bb_width": float(width),
#                     "bb_height": float(height),
#                     "bb_x_min": float(x_min),
#                     "bb_y_min": float(y_min),
#                     "bb_x_max": float(x_max),
#                     "bb_y_max": float(y_max),
#                     "bb_x_bottom_center": float(x_center),
#                     "bb_y_bottom_center": float(y_bottom_center),
#                     "bb_x_top_center": float(x_center),
#                     "bb_y_top_center": float(y_top_center)
#                 })
#         return {"id": "1", "output": result, "ready": True}
#         # return result


