import os
from ultralytics import YOLO

# Get the absolute path to this file's directory (galaxy_object_detection_core/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def model_path(relative_path):
    """Return the full path to a model given its relative path from this script."""
    return os.path.join(BASE_DIR, relative_path)

class GalaxyObjectDetector:
    @staticmethod
    def detect_object(model_relative_path, input_image_path):
        model_full_path = model_path(model_relative_path)
        model_name = os.path.splitext(os.path.basename(model_full_path))[0]
        output_dir = "images_detected"
        os.makedirs(output_dir, exist_ok=True)
        filename_without_ext = os.path.splitext(os.path.basename(input_image_path))[0]
        output_path = os.path.join(output_dir, f"result_of_{filename_without_ext}_using_{model_name}.jpg")
        model = YOLO(model_full_path)
        results = model([input_image_path])
        for result in results:
            result.save(filename=output_path)
        return output_path

    @staticmethod
    def segment_object(model_relative_path, input_image_path):
        return GalaxyObjectDetector.detect_object(model_relative_path, input_image_path)

    @staticmethod
    def detect_human_head(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_human_head_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def detect_invoice_and_receipt(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_invoice_and_receipt_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def detect_ktp(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_ktp_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def detect_medaka_fish(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_medaka_fish_detector.pt", input_image_path)

    @staticmethod
    def detect_meterai(input_image_path, version='latest'):
        version_map = {
            'v1': "models/model_meterai_detector_yolo8n_v1.pt",
            'v2': "models/model_meterai_detector_yolo8n_v2.pt",
            'latest': "models/model_meterai_detector_yolo8n_v2.pt"
        }
        model_relative = version_map.get(version, version_map['latest'])
        return GalaxyObjectDetector.detect_object(model_relative, input_image_path)

    @staticmethod
    def detect_mineral_boulder(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_mineral_boulder_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def segment_mineral_boulder(input_image_path):
        return GalaxyObjectDetector.segment_object("models/model_mineral_boulder_segmentator_yolo8n.pt.pt", input_image_path)

    @staticmethod
    def detect_mineral_soil(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_mineral_soil_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def detect_people(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_people_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def detect_ppe(input_image_path, version='latest'):
        version_map = {
            'v1': "models/model_personal_protective_equipment_detector_yolo8n_v1.pt",
            'v2': "models/model_personal_protective_equipment_detector_yolo8n_v2.pt",
            'latest': "models/model_personal_protective_equipment_detector_yolo8n_v2.pt"
        }
        model_relative = version_map.get(version, version_map['latest'])
        return GalaxyObjectDetector.detect_object(model_relative, input_image_path)

    @staticmethod
    def segment_ppe(input_image_path):
        return GalaxyObjectDetector.segment_object("models/model_personal_protective_equipment_segmentator_yolo8n_v2.pt", input_image_path)

    @staticmethod
    def detect_product_fmcg(input_image_path, version='latest'):
        version_map = {
            'v1': "models/model_product_fmcg_detector_yolo11n_v1.pt",
            'v3': "models/model_product_fmcg_detector_yolo11n_v3.pt",
            'latest': "models/model_product_fmcg_detector_yolo11n_v3.pt"
        }
        model_relative = version_map.get(version, version_map['latest'])
        return GalaxyObjectDetector.detect_object(model_relative, input_image_path)

    @staticmethod
    def detect_qrcode(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_qrcode_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def detect_road_damage(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_road_damage_detector_yolo8n.pt", input_image_path)

    @staticmethod
    def detect_vehicle(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_vehicle_detector_yolo11n_v1.pt", input_image_path)

    @staticmethod
    def detect_vehicle_plate(input_image_path):
        return GalaxyObjectDetector.detect_object("models/model_vehicle_plate_detector_yolo8n_v1.pt", input_image_path)

    @staticmethod
    def detect_custom_object(input_image_path, list_object_to_detect):
        model_relative = "models/yolov8s-world.pt"
        model_full_path = model_path(model_relative)
        output_dir = "images_detected"
        os.makedirs(output_dir, exist_ok=True)
        filename_without_ext = os.path.splitext(os.path.basename(input_image_path))[0]
        model_tag = "_".join(list_object_to_detect)
        output_path = os.path.join(output_dir, f"result_of_{filename_without_ext}_using_custom_detect_{model_tag}.jpg")
        model = YOLO(model_full_path)
        model.set_classes(list_object_to_detect)
        results = model.predict(input_image_path)
        results[0].save(filename=output_path)
        return output_path
