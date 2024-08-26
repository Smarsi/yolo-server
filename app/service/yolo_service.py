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
        self.entry_fifo = queue.Queue()
        self.output_fifo = queue.Queue()
        self.threads = []

        self.running = False
        log_writer(self.log_file, f"Service - YOLO Service started successfully. (Called from __init__)")

    def start_service(self) -> None:
        log_writer(self.log_file, f"Service - Starting YOLO Service.")
        self.running = True

        # Load Classes File
        with open(self.classes_file, "r") as file:
            self.classes = [line.strip() for line in file.readlines()]

        while len(self.threads) < self.instances_quantity:
            log_writer(self.log_file, f"Service - Starting YOLO Service Thread. Threads: {len(self.threads)}")
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
        log_writer(self.log_file, f"Service - YOLO Service started successfully. (Called from run)")
        while(self.running):
            try:
                data = self.entry_fifo.get(timeout=1)
                img = data["img"]
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
                self.output_fifo.put({"output": result, "ready": True, "timestamp": datetime.now().time()})
            except queue.Empty:
                continue
            except Exception as e:
                self.output_fifo.put({"output": [], "ready": False, "timestamp": datetime.now().time()})
                log_writer(self.log_file, f"Service - Error: {e}")
                continue

    def add_frame(self, img: np.ndarray):
        self.entry_fifo.put({"img": img})
        return
    
    def get_result(self) -> dict:
        try:
            result = self.output_fifo.get(timeout=5)  # Ajuste o timeout conforme necessário
            return result
        except queue.Empty:
            return {"output": [], "ready": False, "timestamp": datetime.now().time()}


class newYolo_Service:

    def __init__(self, model_path: str, classes_path: str):
        self.model_path = model_path
        self.net = None
        self._load_model()
        with open(classes_path, "r") as file:
            self.classes = [line.strip() for line in file.readlines()]

    def _load_model(self):
        self.net = cv2.dnn.readNetFromONNX(self.model_path)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    def get_model(self):
        return self.net
    
    def perform_inference(self, image: np.ndarray):
        result = []
        blob = cv2.dnn.blobFromImage(image, 1/255, (640, 640), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward()
        
        result = []
        boxes = []
        confidences = []
        class_ids = []
        confidence_threshold = 0.5
        nms_threshold = 0.4

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
        return {"id": "1", "output": result, "ready": True, "timestamp": datetime.now().time()}
        # return result


