import cv2
import torch
import torchvision.transforms as T
import numpy as np
from PIL import Image
from collections import defaultdict
import torch.nn.functional as F
import time
from Memento.models import RecognitionModel, DetectionModel

def live_recognition(model, detector, device='cuda', add_face_key='a', rec_conf_thresh=0.5, det_conf_thresh=0.8):
    model.eval().to(device)
    detector.eval()
    known_faces = {}  # name -> embedding
    transform = T.Compose([
        T.Resize((256, 256)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    cap = cv2.VideoCapture(0)
    print("[INFO] Press 'a' to add a face, 'q' to quit.")

    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        orig = frame.copy()
        orig_h, orig_w = frame.shape[:2]

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_tensor = torch.from_numpy(frame_rgb).permute(2,0,1).unsqueeze(0).float() / 255.
        frame_tensor = frame_tensor.to(device)
        frame_resized = F.interpolate(frame_tensor, size=(256,256), mode='bilinear', align_corners=False)

        with torch.inference_mode():
            boxes = detector.predict_tensor(frame_resized)[0]

        scale_x = orig_w / 256
        scale_y = orig_h / 256
        detected_faces = []

        for (cx, cy, w, h, conf) in boxes:
            if conf < det_conf_thresh:
                continue
            x1 = int((cx - w / 2) * scale_x)
            y1 = int((cy - h / 2) * scale_y)
            x2 = int((cx + w / 2) * scale_x)
            y2 = int((cy + h / 2) * scale_y)

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(orig_w - 1, x2), min(orig_h - 1, y2)

            face_img = orig[y1:y2, x1:x2]
            face_pil = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
            face_tensor = transform(face_pil).unsqueeze(0).to(device)

            with torch.no_grad():
                embedding = model(face_tensor).cpu().squeeze(0)

            name = "Unknown"
            best_sim = 0.0
            for known_name, known_emb in known_faces.items():
                sim = F.cosine_similarity(embedding.unsqueeze(0), known_emb.unsqueeze(0)).item()
                if sim > rec_conf_thresh and sim > best_sim:
                    best_sim = sim
                    name = f"{known_name} ({sim:.2f})"

            detected_faces.append(((x1, y1, x2, y2), name))

        for (x1, y1, x2, y2), name in detected_faces:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        inf_time = (time.time() - start_time) * 1000
        cv2.putText(frame, f"Inference: {inf_time:.1f} ms", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("Live Recognition", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(add_face_key):
            if len(detected_faces) == 1:
                (x1, y1, x2, y2), _ = detected_faces[0]
                face_img = orig[y1:y2, x1:x2]
                face_pil = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
                face_tensor = transform(face_pil).unsqueeze(0).to(device)
                with torch.no_grad():
                    embedding = model(face_tensor).cpu().squeeze(0)

                name = input("Enter name for this face: ").strip()
                if name:
                    known_faces[name] = embedding
                    print(f"[INFO] Added face for: {name}")
            else:
                print("[WARNING] Add failed: No face or multiple faces detected.")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



