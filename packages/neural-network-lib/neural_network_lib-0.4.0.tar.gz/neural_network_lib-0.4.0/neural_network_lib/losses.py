import cupy as cp


class MeanSquaredError:
    def __call__(self, y_true, y_pred):
        return cp.mean((y_true - y_pred) ** 2)  # Без .get()

    def gradient(self, y_true, y_pred):
        return 2 * (y_pred - y_true) / y_true.size


class CrossEntropyLoss:
    def __call__(self, y_true, y_pred):
        y_pred = cp.clip(y_pred, 1e-7, 1 - 1e-7)
        batch_size = y_true.shape[0]
        return -cp.sum(y_true * cp.log(y_pred)) / batch_size

    def gradient(self, y_true, y_pred):
        batch_size = y_true.shape[0]
        return (y_pred - y_true) / batch_size


class HingeLoss:
    def __call__(self, y_true, y_pred):
        return cp.mean(cp.maximum(0, 1 - y_true * y_pred))

    def gradient(self, y_true, y_pred):
        return cp.where(y_true * y_pred < 1, -y_true, 0)


class YOLOLoss:
    """Класс для вычисления функции потерь YOLO (You Only Look Once) для задач детекции объектов."""

    def __init__(self, S, B, C, lambda_coord=5.0, lambda_noobj=0.5):
        self.S = S
        self.B = B
        self.C = C
        self.lambda_coord = lambda_coord
        self.lambda_noobj = lambda_noobj

    def __call__(self, y_true, y_pred):
        batch_size = y_true.shape[0]
        y_pred = y_pred.reshape(batch_size, self.S, self.S, self.B * 5 + self.C)

        pred_boxes = y_pred[..., :self.B * 5].reshape(-1, self.S, self.S, self.B, 5)
        pred_classes = y_pred[..., self.B * 5:].reshape(-1, self.S, self.S, self.C)
        true_boxes = y_true[..., :self.B * 5].reshape(-1, self.S, self.S, self.B, 5)
        true_classes = y_true[..., self.B * 5:].reshape(-1, self.S, self.S, self.C)

        obj_mask = true_boxes[..., 4] == 1
        obj_mask = cp.any(obj_mask, axis=3)
        noobj_mask = ~obj_mask

        coord_loss = self.lambda_coord * cp.sum(
            (pred_boxes[..., :4] - true_boxes[..., :4]) ** 2 * obj_mask[..., None, None]
        )

        conf_obj_loss = cp.sum(
            (pred_boxes[..., 4] - true_boxes[..., 4]) ** 2 * obj_mask[..., None]
        )

        conf_noobj_loss = self.lambda_noobj * cp.sum(
            (pred_boxes[..., 4] - true_boxes[..., 4]) ** 2 * noobj_mask[..., None]
        )

        class_loss = cp.sum(
            (pred_classes - true_classes) ** 2 * obj_mask[..., None]
        )

        total_loss = coord_loss + conf_obj_loss + conf_noobj_loss + class_loss
        return total_loss / batch_size

    def gradient(self, y_true, y_pred):
        batch_size = y_true.shape[0]
        y_pred = y_pred.reshape(batch_size, self.S, self.S, self.B * 5 + self.C)
        y_pred = cp.clip(y_pred, -10, 10)
        pred_boxes = y_pred[..., :self.B * 5].reshape(-1, self.S, self.S, self.B, 5)
        pred_classes = y_pred[..., self.B * 5:].reshape(-1, self.S, self.S, self.C)
        true_boxes = y_true[..., :self.B * 5].reshape(-1, self.S, self.S, self.B, 5)
        true_classes = y_true[..., self.B * 5:].reshape(-1, self.S, self.S, self.C)

        obj_mask = true_boxes[..., 4] == 1
        obj_mask = cp.any(obj_mask, axis=3)
        noobj_mask = ~obj_mask

        grad = cp.zeros_like(y_pred)
        grad_boxes = grad[..., :self.B * 5].reshape(-1, self.S, self.S, self.B, 5)
        grad_classes = grad[..., self.B * 5:].reshape(-1, self.S, self.S, self.C)

        grad_boxes[..., :4] = 2 * self.lambda_coord * (pred_boxes[..., :4] - true_boxes[..., :4]) * obj_mask[
            ..., None, None]
        grad_boxes[..., 4] = 2 * (pred_boxes[..., 4] - true_boxes[..., 4]) * obj_mask[..., None]

        grad_boxes[..., 4] += 2 * self.lambda_noobj * (pred_boxes[..., 4] - true_boxes[..., 4]) * noobj_mask[..., None]
        grad_classes[...] = 2 * (pred_classes - true_classes) * obj_mask[..., None]

        grad = cp.clip(grad, -100, 100)
        return grad / batch_size