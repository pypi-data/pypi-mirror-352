from galaxy_object_detection_core.GalaxyObjectDetector import GalaxyObjectDetector

if __name__ == "__main__":
    test_image = "images_sample/head.jpeg"  # Change to your actual image path

    result_path = GalaxyObjectDetector.detect_human_head(test_image)
    print("Human Head Detection:", result_path)

    result_path = GalaxyObjectDetector.detect_ppe(test_image, version="v2")
    print("PPE Detection (v2):", result_path)

    result_path = GalaxyObjectDetector.segment_ppe(test_image)
    print("PPE Segmentation:", result_path)

    result_path = GalaxyObjectDetector.detect_custom_object(test_image, ["helmet", "person"])
    print("Custom Object Detection:", result_path)