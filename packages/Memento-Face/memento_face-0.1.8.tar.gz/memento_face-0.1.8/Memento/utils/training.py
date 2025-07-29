import torch
import torch.nn.functional as F
import time

def compute_iou(preds, targets, threshold=0.5):
    B, _, H, W = preds.shape
    preds = preds.permute(0, 2, 3, 1).reshape(-1, 4)
    targets = targets.permute(0, 2, 3, 1).reshape(-1, 4)

    pred_x1 = preds[:, 0] - preds[:, 2] / 2
    pred_y1 = preds[:, 1] - preds[:, 3] / 2
    pred_x2 = preds[:, 0] + preds[:, 2] / 2
    pred_y2 = preds[:, 1] + preds[:, 3] / 2

    targ_x1 = targets[:, 0] - targets[:, 2] / 2
    targ_y1 = targets[:, 1] - targets[:, 3] / 2
    targ_x2 = targets[:, 0] + targets[:, 2] / 2
    targ_y2 = targets[:, 1] + targets[:, 3] / 2

    inter_x1 = torch.max(pred_x1, targ_x1)
    inter_y1 = torch.max(pred_y1, targ_y1)
    inter_x2 = torch.min(pred_x2, targ_x2)
    inter_y2 = torch.min(pred_y2, targ_y2)

    inter_area = (inter_x2 - inter_x1).clamp(0) * (inter_y2 - inter_y1).clamp(0)
    pred_area = (pred_x2 - pred_x1).clamp(0) * (pred_y2 - pred_y1).clamp(0)
    targ_area = (targ_x2 - targ_x1).clamp(0) * (targ_y2 - targ_y1).clamp(0)

    union_area = pred_area + targ_area - inter_area + 1e-6
    iou = inter_area / union_area
    return (iou > threshold).float().mean().item()

def format_time(seconds: float) -> str:
    """Format seconds to 1 decimal place with 's' suffix."""
    return f"{seconds:.1f}s"

def smooth_ema(old, new, alpha=0.1):
    """Exponential moving average smoothing."""
    if old is None:
        return new
    return old * (1 - alpha) + new * alpha

def train_detection(model, train_dl, val_dl=None, epochs=20, lr=1e-3, device="cuda", save_checkpoint=True, manual_seed=69):
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    torch.manual_seed(manual_seed)
    torch.cuda.manual_seed_all(manual_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        total_iou = 0.0
        total_batches = 0
        train_start = time.time()
        avg_batch_time = None  # for smoothing ETA

        for i, (imgs, targets) in enumerate(train_dl):
            batch_start = time.time()
            imgs = imgs.to(device)
            targets = targets.to(device)

            preds = model(imgs)
            bbox_preds = preds[:, :4, :, :]
            obj_preds = preds[:, 4:, :, :]
            bbox_targets = targets[:, :4, :, :]
            obj_targets = targets[:, 4:, :, :]

            bbox_loss = F.mse_loss(bbox_preds, bbox_targets)
            obj_loss = F.binary_cross_entropy_with_logits(obj_preds, obj_targets)
            loss = bbox_loss + obj_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            total_iou += compute_iou(bbox_preds, bbox_targets)
            total_batches += 1

            batch_time = time.time() - batch_start
            avg_batch_time = smooth_ema(avg_batch_time, batch_time, alpha=0.1)

            batches_left = len(train_dl) - (i + 1)
            est_time_left = avg_batch_time * batches_left
            elapsed_time = time.time() - train_start

            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {total_loss / total_batches:.4f} | "
                f"Train IoU: {total_iou / total_batches:.4f} | "
                f"Batch: {i+1}/{len(train_dl)} | "
                f"Elapsed: {format_time(elapsed_time)} | "
                f"ETA: {format_time(est_time_left)}",
                end='\r'
            )

        print()
        avg_train_loss = total_loss / len(train_dl)
        avg_train_iou = total_iou / len(train_dl)

        if val_dl is not None:
            model.eval()
            val_loss = 0.0
            val_iou = 0.0
            val_batches = 0
            val_start = time.time()
            avg_val_batch_time = None

            with torch.inference_mode():
                for i, (imgs, targets) in enumerate(val_dl):
                    batch_start = time.time()
                    imgs = imgs.to(device)
                    targets = targets.to(device)

                    preds = model(imgs)
                    bbox_preds = preds[:, :4, :, :]
                    obj_preds = preds[:, 4:, :, :]
                    bbox_targets = targets[:, :4, :, :]
                    obj_targets = targets[:, 4:, :, :]

                    bbox_loss = F.mse_loss(bbox_preds, bbox_targets)
                    obj_loss = F.binary_cross_entropy_with_logits(obj_preds, obj_targets)
                    loss = bbox_loss + obj_loss

                    val_loss += loss.item()
                    val_iou += compute_iou(bbox_preds, bbox_targets)
                    val_batches += 1

                    batch_time = time.time() - batch_start
                    avg_val_batch_time = smooth_ema(avg_val_batch_time, batch_time, alpha=0.1)

                    batches_left = len(val_dl) - (i + 1)
                    est_time_left = avg_val_batch_time * batches_left
                    elapsed_time = time.time() - val_start

                    print(
                        f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                        f"Val Loss: {val_loss / val_batches:.4f} | "
                        f"Val IoU: {val_iou / val_batches:.4f} | "
                        f"Batch: {i+1}/{len(val_dl)} | "
                        f"Elapsed: {format_time(elapsed_time)} | "
                        f"ETA: {format_time(est_time_left)}",
                        end='\r'
                    )

            print()
            avg_val_loss = val_loss / len(val_dl)
            avg_val_iou = val_iou / len(val_dl)
            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {avg_train_loss:.4f} | Train IoU: {avg_train_iou:.4f} || "
                f"Val Loss: {avg_val_loss:.4f} | Val IoU: {avg_val_iou:.4f}"
            )
        else:
            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {avg_train_loss:.4f} | Train IoU: {avg_train_iou:.4f}"
            )

        if save_checkpoint:
            torch.save(model.state_dict(), f"DetectionWeights_epoch{epoch+1}.pth")

    return model

def smooth_ema(prev_value, new_value, alpha=0.1):
    if prev_value is None:
        return new_value
    return alpha * new_value + (1 - alpha) * prev_value

def format_time(seconds):
    """Convert seconds to a formatted time string (e.g., '1h 23m 45s')."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
import time
from torchvision import models


def train_recognition(model, train_dl, val_dl=None, epochs=20, lr=1e-3, device="cuda", save_checkpoint=True, manual_seed=69):
    """Train a face recognition model with ArcFace loss."""
    model.to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    criterion = nn.CrossEntropyLoss()  # Suitable for ArcFace logits
    scaler = torch.amp.GradScaler('cuda')  # Updated for mixed precision

    # Set random seeds for reproducibility
    torch.manual_seed(manual_seed)
    torch.cuda.manual_seed_all(manual_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    best_val_sim = -float('inf')
    best_epoch = 0

    for epoch in range(epochs):
        # Training phase
        model.train()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        train_start = time.time()
        avg_batch_time = None

        for i, (imgs, labels) in enumerate(train_dl):
            batch_start = time.time()
            imgs = imgs.to(device)
            labels = labels.to(device)

            with torch.amp.autocast('cuda'):  # Updated API
                logits = model(imgs, labels)  # Call model directly with labels
                loss = criterion(logits, labels)

            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item()
            preds = logits.argmax(dim=1)
            total_correct += (preds == labels).sum().item()
            total_samples += labels.size(0)

            batch_time = time.time() - batch_start
            avg_batch_time = smooth_ema(avg_batch_time, batch_time)
            batches_left = len(train_dl) - (i + 1)
            est_time_left = avg_batch_time * batches_left
            elapsed_time = time.time() - train_start

            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {total_loss / (i+1):.4f} | "
                f"Train Acc: {100 * total_correct / total_samples:6.2f}% | "
                f"Batch: {i+1}/{len(train_dl)} | "
                f"Elapsed: {format_time(elapsed_time)} | "
                f"ETA: {format_time(est_time_left)}",
                end='\r'
            )

        print()  # Newline after training progress
        avg_train_loss = total_loss / len(train_dl)
        train_acc = total_correct / total_samples * 100
        scheduler.step()

        # Validation phase (if validation dataloader is provided)
        if val_dl is not None:
            model.eval()
            val_loss = 0.0
            val_correct = 0
            val_samples = 0
            val_same_sim = 0.0
            val_diff_sim = 0.0
            val_batches = 0
            val_start = time.time()
            avg_val_batch_time = None

            with torch.inference_mode():
                for i, (imgs, labels) in enumerate(val_dl):
                    batch_start = time.time()
                    imgs = imgs.to(device)
                    labels = labels.to(device)

                    with torch.amp.autocast('cuda'):  # Updated API
                        embeddings = model(imgs)  # Get embeddings without labels
                        logits = model(imgs, labels)  # Get logits with labels
                        loss = criterion(logits, labels)

                    val_loss += loss.item()
                    preds = logits.argmax(dim=1)
                    val_correct += (preds == labels).sum().item()
                    val_samples += labels.size(0)

                    same_sim, diff_sim = F.cosine_similarity(embeddings, labels)
                    val_same_sim += same_sim
                    val_diff_sim += diff_sim
                    val_batches += 1

                    batch_time = time.time() - batch_start
                    avg_val_batch_time = smooth_ema(avg_val_batch_time, batch_time)
                    batches_left = len(val_dl) - (i + 1)
                    est_time_left = avg_val_batch_time * batches_left
                    elapsed_time = time.time() - val_start

                    print(
                        f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                        f"Val Loss: {val_loss / (i+1):.4f} | "
                        f"Val Acc: {100 * val_correct / val_samples:6.2f}% | "
                        f"Batch: {i+1}/{len(val_dl)} | "
                        f"Elapsed: {format_time(elapsed_time)} | "
                        f"ETA: {format_time(est_time_left)}",
                        end='\r'
                    )

            print()  # Newline after validation progress
            avg_val_loss = val_loss / len(val_dl)
            avg_val_acc = val_correct / val_samples * 100
            avg_val_same_sim = val_same_sim / val_batches
            avg_val_diff_sim = val_diff_sim / val_batches

            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}% || "
                f"Val Loss: {avg_val_loss:.4f} | Val Acc: {avg_val_acc:.2f}% || "
                f"Val Same Sim: {avg_val_same_sim:.4f} | Val Diff Sim: {avg_val_diff_sim:.4f}"
            )

            # Save best model based on same-face similarity
            if avg_val_same_sim > best_val_sim:
                best_val_sim = avg_val_same_sim
                best_epoch = epoch
                if save_checkpoint:
                    torch.save(model.state_dict(), "best_model.pth")

        else:
            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}%"
            )

        if save_checkpoint and val_dl is None:
            torch.save(model.state_dict(), f"RecognitionWeights_epoch{epoch+1}.pth")

    if val_dl is not None:
        print(f"Best validation same similarity: {best_val_sim:.4f} at epoch {best_epoch+1}")
    return model