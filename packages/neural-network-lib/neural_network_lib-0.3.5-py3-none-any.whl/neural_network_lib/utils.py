import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def compute_iou(box, boxes):

    x1 = cp.maximum(box[0], boxes[:, 0])
    y1 = cp.maximum(box[1], boxes[:, 1])
    x2 = cp.minimum(box[2], boxes[:, 2])
    y2 = cp.minimum(box[3], boxes[:, 3])
    inter_area = cp.clip(x2 - x1, 0, 1) * cp.clip(y2 - y1, 0, 1)
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    return inter_area / (box_area + boxes_area - inter_area + 1e-8)


def nms(boxes, scores, iou_threshold):
    if boxes is None or len(boxes) == 0 or scores is None or len(scores) == 0:
        return cp.array([]), cp.array([])

    indices = cp.argsort(-scores)
    boxes = boxes[indices]
    scores = scores[indices]

    keep = []
    while len(indices) > 0:
        keep.append(indices[0])
        if len(indices) == 1:
            break

        x1 = cp.maximum(boxes[0, 0], boxes[1:, 0])
        y1 = cp.maximum(boxes[0, 1], boxes[1:, 1])
        x2 = cp.minimum(boxes[0, 2], boxes[1:, 2])
        y2 = cp.minimum(boxes[0, 3], boxes[1:, 3])

        inter_area = cp.clip(x2 - x1, 0, None) * cp.clip(y2 - y1, 0, None)
        box_area = (boxes[0, 2] - boxes[0, 0]) * (boxes[0, 3] - boxes[0, 1])
        other_areas = (boxes[1:, 2] - boxes[1:, 0]) * (boxes[1:, 3] - boxes[1:, 1])
        iou = inter_area / (box_area + other_areas - inter_area + 1e-6)

        indices = indices[1:][iou < iou_threshold]
        boxes = boxes[1:][iou < iou_threshold]
        scores = scores[1:][iou < iou_threshold]

    if len(keep) == 0:
        return cp.array([]), cp.array([])

    return boxes[keep], scores[keep]

def postprocess(outputs, conf_threshold=0.5, image_size=224, grid_size=7, num_boxes=1, num_classes=20):
    batch_size = outputs.shape[0]
    boxes, scores, classes = [], [], []

    for b in range(batch_size):
        batch_boxes, batch_scores, batch_classes = [], [], []
        for i in range(grid_size):
            for j in range(grid_size):
                for k in range(num_boxes):
                    conf = outputs[b, i, j, k * 5 + 4]
                    if conf > conf_threshold:
                        x, y, w, h = outputs[b, i, j, k * 5:k * 5 + 4]
                        x_min = (x - w / 2) * image_size
                        y_min = (y - h / 2) * image_size
                        x_max = (x + w / 2) * image_size
                        y_max = (y + h / 2) * image_size
                        batch_boxes.append([x_min, y_min, x_max, y_max])
                        batch_scores.append(conf)
                        class_probs = outputs[b, i, j, num_boxes * 5:]
                        batch_classes.append(cp.argmax(class_probs).item())
        if batch_boxes:
            batch_boxes = cp.array(batch_boxes)
            batch_scores = cp.array(batch_scores)
            keep = nms(batch_boxes, batch_scores, iou_threshold=0.5)
            boxes.append(batch_boxes[keep])
            scores.append(batch_scores[keep])
            classes.append(cp.array([batch_classes[i] for i in keep]))
        else:
            boxes.append(cp.array([]))
            scores.append(cp.array([]))
            classes.append(cp.array([]))

    return boxes, scores, classes


def compute_map(model, x_val, y_val, conf_threshold, iou_threshold, NUM_CLASSES, GRID_SIZE, NUM_BOXES, IMAGE_SIZE):
    all_boxes = []
    all_scores = []
    all_classes = []
    all_gt_boxes = []
    all_gt_classes = []

    for i in range(0, x_val.shape[0], 1):
        img = x_val[i:i + 1]
        target = y_val[i:i + 1]

        pred = model.forward(img, training=False)

        boxes = []
        scores = []
        classes = []

        for grid_x in range(GRID_SIZE):
            for grid_y in range(GRID_SIZE):
                for b in range(NUM_BOXES):
                    conf = pred[0, grid_y, grid_x, b * 5 + 4]
                    if conf > conf_threshold:
                        x = pred[0, grid_y, grid_x, b * 5]
                        y = pred[0, grid_y, grid_x, b * 5 + 1]
                        w = pred[0, grid_y, grid_x, b * 5 + 2]
                        h = pred[0, grid_y, grid_x, b * 5 + 3]

                        x_min = (x - w / 2) * IMAGE_SIZE
                        x_max = (x + w / 2) * IMAGE_SIZE
                        y_min = (y - h / 2) * IMAGE_SIZE
                        y_max = (y + h / 2) * IMAGE_SIZE

                        if x_min >= x_max or y_min >= y_max:
                            continue

                        class_probs = pred[0, grid_y, grid_x, NUM_BOXES * 5:NUM_BOXES * 5 + NUM_CLASSES]
                        class_idx = cp.argmax(class_probs)

                        boxes.append([x_min, y_min, x_max, y_max])
                        scores.append(conf)
                        classes.append(class_idx)

        boxes = cp.array(boxes) if boxes else None
        scores = cp.array(scores) if scores else None
        classes = cp.array(classes) if classes else None

        if boxes is not None and len(boxes) > 0 and scores is not None and len(scores) > 0:
            boxes, scores = nms(boxes, scores, iou_threshold)
            classes = classes[:len(boxes)] if classes is not None and len(boxes) > 0 else None
            print(f"После NMS: {len(boxes) if boxes is not None else 0} боксов")
        else:
            boxes = None
            scores = None
            classes = None
            print("Пропущен NMS: нет боксов или оценок")

        gt_boxes = []
        gt_classes = []
        for grid_x in range(GRID_SIZE):
            for grid_y in range(GRID_SIZE):
                for b in range(NUM_BOXES):
                    conf = target[0, grid_y, grid_x, b * 5 + 4]
                    if conf > 0:
                        x = target[0, grid_y, grid_x, b * 5]
                        y = target[0, grid_y, grid_x, b * 5 + 1]
                        w = target[0, grid_y, grid_x, b * 5 + 2]
                        h = target[0, grid_y, grid_x, b * 5 + 3]

                        x_min = (x - w / 2) * IMAGE_SIZE
                        x_max = (x + w / 2) * IMAGE_SIZE
                        y_min = (y - h / 2) * IMAGE_SIZE
                        y_max = (y + h / 2) * IMAGE_SIZE

                        class_probs = target[0, grid_y, grid_x, NUM_BOXES * 5:NUM_BOXES * 5 + NUM_CLASSES]
                        class_idx = cp.argmax(class_probs)

                        gt_boxes.append([x_min, y_min, x_max, y_max])
                        gt_classes.append(class_idx)

        all_boxes.append(boxes)
        all_scores.append(scores)
        all_classes.append(classes)
        all_gt_boxes.append(cp.array(gt_boxes) if gt_boxes else None)
        all_gt_classes.append(cp.array(gt_classes) if gt_classes else None)

    ap_sum = 0
    for class_id in range(NUM_CLASSES):
        true_positives = []
        false_positives = []
        num_gt = 0.0

        for i in range(len(all_boxes)):
            pred_boxes = all_boxes[i]
            pred_scores = all_scores[i]
            pred_classes = all_classes[i]
            gt_boxes = all_gt_boxes[i]
            gt_classes = all_gt_classes[i]

            if pred_boxes is not None and pred_classes is not None and len(pred_boxes) > 0 and len(pred_classes) > 0:
                class_mask = pred_classes == class_id
                if len(class_mask) != len(pred_boxes):
                    print(f"Предупреждение: Несоответствие размеров: class_mask={len(class_mask)}, pred_boxes={len(pred_boxes)}")
                    continue
                class_boxes = pred_boxes[class_mask] if cp.any(class_mask) else None
                class_scores = pred_scores[class_mask] if cp.any(class_mask) else None
            else:
                class_boxes = None
                class_scores = None

            if class_scores is not None and len(class_scores) > 0:
                sorted_indices = cp.argsort(-class_scores)
                class_boxes = class_boxes[sorted_indices] if class_boxes is not None else None
                class_scores = class_scores[sorted_indices]

            gt_mask = gt_classes == class_id if gt_classes is not None else cp.array([])
            num_gt += cp.sum(gt_mask)

            detected = cp.zeros(len(gt_boxes) if gt_boxes is not None else 0, dtype=cp.bool_)

            if class_boxes is not None and len(class_boxes) > 0:
                for j in range(len(class_boxes)):
                    pred_box = class_boxes[j]
                    max_iou = 0
                    max_idx = -1

                    if gt_boxes is not None:
                        for k in range(len(gt_boxes)):
                            if gt_classes[k] == class_id and not detected[k]:
                                x1 = cp.maximum(pred_box[0], gt_boxes[k][0])
                                y1 = cp.maximum(pred_box[1], gt_boxes[k][1])
                                x2 = cp.minimum(pred_box[2], gt_boxes[k][2])
                                y2 = cp.minimum(pred_box[3], gt_boxes[k][3])

                                inter_area = cp.clip(x2 - x1, 0, IMAGE_SIZE) * cp.clip(y2 - y1, 0, IMAGE_SIZE)
                                pred_area = (pred_box[2] - pred_box[0]) * (pred_box[3] - pred_box[1])
                                gt_area = (gt_boxes[k][2] - gt_boxes[k][0]) * (gt_boxes[k][3] - gt_boxes[k][1])

                                union_area = pred_area + gt_area - inter_area
                                iou = inter_area / (union_area + 1e-6)

                                if iou > max_iou:
                                    max_iou = iou
                                    max_idx = k

                    if max_iou >= iou_threshold and max_idx >= 0:
                        true_positives.append(1)
                        false_positives.append(0)
                        detected[max_idx] = True
                    else:
                        true_positives.append(0)
                        false_positives.append(1)

        if num_gt == 0:
            continue

        true_positives = cp.array(true_positives)
        false_positives = cp.array(false_positives)

        cum_tp = cp.cumsum(true_positives)
        cum_fp = cp.cumsum(false_positives)

        precision = cum_tp / (cum_tp + cum_fp + 1e-6)
        recall = cum_tp / num_gt

        ap = 0
        for t in cp.linspace(0, 1, 11):
            mask = recall >= t
            if cp.any(mask):
                ap += cp.max(precision[mask]) / 11

        ap_sum += ap

    mAP = ap_sum / NUM_CLASSES if NUM_CLASSES > 0 else 0
    return float(mAP.get())


def visualize_detections(image, pred_boxes, pred_scores, pred_classes, gt_boxes, gt_classes, class_names,
                         image_size=224, conf_threshold=0.5, show_gt=True, title="Detection Results"):
    """
    Визуализирует предсказанные и истинные bounding box'ы на изображении.

    Аргументы:
        image: CuPy массив (H, W, C) - изображение в формате NHWC
        pred_boxes: CuPy массив (N, 4) - предсказанные боксы [x_min, y_min, x_max, y_max]
        pred_scores: CuPy массив (N,) - уверенности предсказанных боксов
        pred_classes: CuPy массив (N,) - классы предсказанных боксов
        gt_boxes: CuPy массив (M, 4) - истинные боксы [x_min, y_min, x_max, y_max]
        gt_classes: CuPy массив (M,) - классы истинных боксов
        class_names: список строк - названия классов
        image_size: int - размер изображения (для масштабирования)
        conf_threshold: float - порог уверенности для предсказанных боксов
        show_gt: bool - показывать ли истинные боксы
        title: str - заголовок графика
    """
    image = image.get() if isinstance(image, cp.ndarray) else image
    if image.max() <= 1.0:
        image = (image * 255).astype(np.uint8)

    fig, ax = plt.subplots(1, figsize=(8, 8))
    ax.imshow(image)

    if pred_boxes is not None and pred_scores is not None and pred_classes is not None:
        for box, score, cls in zip(pred_boxes, pred_scores, pred_classes):
            score = score.get() if isinstance(score, cp.ndarray) else score
            if score > conf_threshold:
                x_min, y_min, x_max, y_max = box.get() if isinstance(box, cp.ndarray) else box
                width = x_max - x_min
                height = y_max - y_min
                if width <= 0 or height <= 0:
                    continue

                rect = patches.Rectangle((x_min, y_min), width, height,
                                         linewidth=2, edgecolor='r', facecolor='none', label='Predicted')
                ax.add_patch(rect)
                cls_idx = int(cls.get() if isinstance(cls, cp.ndarray) else cls)
                label = f"{class_names[cls_idx]}: {score:.2f}"
                ax.text(x_min, y_min, label, color='white',
                        bbox=dict(facecolor='red', alpha=0.5))

    if show_gt and gt_boxes is not None and gt_classes is not None:
        for box, cls in zip(gt_boxes, gt_classes):
            x_min, y_min, x_max, y_max = box.get() if isinstance(box, cp.ndarray) else box
            width = x_max - x_min
            height = y_max - y_min
            if width <= 0 or height <= 0:
                continue

            rect = patches.Rectangle((x_min, y_min), width, height,
                                     linewidth=2, edgecolor='g', facecolor='none', label='')
            ax.add_patch(rect)
            cls_idx = int(cls.get() if isinstance(cls, cp.ndarray) else cls)
            label = f"{class_names[cls_idx]}"
            ax.text(x_min, y_min + 10, label, color='white',
                    bbox=dict(facecolor='green', alpha=0.5))

    ax.set_title(title)
    ax.axis('off')

    if (pred_boxes is not None and len(pred_boxes) > 0) or (gt_boxes is not None and len(gt_boxes) > 0):
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    plt.show()


def extract_boxes(pred, target, conf_threshold=0.7, num_classes=3, grid_size=7, num_boxes=1, image_size=224,
                  iou_threshold=0.5):
    """
    Извлекает предсказанные и истинные bounding box'ы из тензоров предсказаний и целевых значений.

    Аргументы:
        pred: CuPy массив (1, S, S, B*5 + C) - предсказания модели
        target: CuPy массив (1, S, S, B*5 + C) - целевые значения
        conf_threshold: float - порог уверенности для предсказанных боксов
        num_classes: int - количество классов (например, 3 для синтетического датасета)
        grid_size: int - размер сетки (S)
        num_boxes: int - количество боксов на ячейку (B)
        image_size: int - размер изображения (например, 224)
        iou_threshold: float - порог IoU для NMS

    Возвращает:
        pred_boxes: CuPy массив (N, 4) или None - предсказанные боксы [x_min, y_min, x_max, y_max]
        pred_scores: CuPy массив (N,) или None - уверенности предсказанных боксов
        pred_classes: CuPy массив (N,) или None - классы предсказанных боксов
        gt_boxes: CuPy массив (M, 4) или None - истинные боксы
        gt_classes: CuPy массив (M,) или None - классы истинных боксов
    """
    pred_boxes = []
    pred_scores = []
    pred_classes = []
    gt_boxes = []
    gt_classes = []

    for grid_x in range(grid_size):
        for grid_y in range(grid_size):
            for b in range(num_boxes):
                conf = pred[0, grid_y, grid_x, b * 5 + 4]
                if conf > conf_threshold:
                    x = pred[0, grid_y, grid_x, b * 5]
                    y = pred[0, grid_y, grid_x, b * 5 + 1]
                    w = pred[0, grid_y, grid_x, b * 5 + 2]
                    h = pred[0, grid_y, grid_x, b * 5 + 3]

                    x_min = (x - w / 2) * image_size
                    x_max = (x + w / 2) * image_size
                    y_min = (y - h / 2) * image_size
                    y_max = (y + h / 2) * image_size

                    if x_min >= x_max or y_min >= y_max:
                        continue

                    class_probs = pred[0, grid_y, grid_x, num_boxes * 5:num_boxes * 5 + num_classes]
                    class_idx = cp.argmax(class_probs)

                    pred_boxes.append([x_min, y_min, x_max, y_max])
                    pred_scores.append(conf)
                    pred_classes.append(class_idx)

    for grid_x in range(grid_size):
        for grid_y in range(grid_size):
            for b in range(num_boxes):
                conf = target[0, grid_y, grid_x, b * 5 + 4]
                if conf > 0:
                    x = target[0, grid_y, grid_x, b * 5]
                    y = target[0, grid_y, grid_x, b * 5 + 1]
                    w = target[0, grid_y, grid_x, b * 5 + 2]
                    h = target[0, grid_y, grid_x, b * 5 + 3]

                    x_min = (x - w / 2) * image_size
                    x_max = (x + w / 2) * image_size
                    y_min = (y - h / 2) * image_size
                    y_max = (y + h / 2) * image_size

                    if x_min >= x_max or y_min >= y_max:
                        continue

                    class_probs = target[0, grid_y, grid_x, num_boxes * 5:num_boxes * 5 + num_classes]
                    class_idx = cp.argmax(class_probs)

                    gt_boxes.append([x_min, y_min, x_max, y_max])
                    gt_classes.append(class_idx)


    boxes = cp.array(pred_boxes) if pred_boxes else None
    scores = cp.array(pred_scores) if pred_scores else None
    classes = cp.array(pred_classes) if pred_classes else None
    if boxes is not None and len(boxes) > 0:
        boxes, scores = nms(boxes, scores, iou_threshold)
        classes = classes[:len(boxes)] if classes is not None else None

    print(f"Pred boxes before NMS: {len(pred_boxes) if pred_boxes else 0}, "
          f"Pred boxes after NMS: {len(boxes) if boxes is not None else 0}, "
          f"GT boxes: {len(gt_boxes) if gt_boxes else 0}")

    return (boxes, scores, classes,
            cp.array(gt_boxes) if gt_boxes else None,
            cp.array(gt_classes) if gt_classes else None)
