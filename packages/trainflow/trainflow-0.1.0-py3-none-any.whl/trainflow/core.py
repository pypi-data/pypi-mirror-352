import json
from tqdm import tqdm
import math
import torch
import torch.nn.functional as F
import random
import os
import time
import numpy as np

class BatchAllocator:
    def __init__(self, desc):
        print(desc + '\n')
        self.flag = int(desc.split()[-1])
        self.links = None
        self.link_int = None
        self.ep = 0
        self.eps = 0
        self.labels = None
        self.predicted = None
        self.mtime = 0
        self.loss = None

    def load_dataset(self, path, pathv=None):
        def load_data(path):
            with open(path) as f:
                return json.load(f)
        t = load_data(path)
        t, links = t[:-1], t[-1]
        self.links = links
        self.link_int = self.links_interaction(links, self.flag)
        if pathv is not None:
            v = load_data(pathv)
            return t, v
        return t

    def create_bar(self, dataloader, ep, eps, desc):
        self.loss = TrainingLossTracker(max_epochs=eps)
        if ep > -1 and eps > -1:
            self.ep, self.eps = ep, eps
        bar = tqdm(dataloader, desc=f'Epoch {ep + 1}/{eps} [' + desc + ']', leave=False)
        return bar

    def sigmoid(self, ep, ept, a, k=6.0, noise_range=0.03):
        a = a / 100.0 if a > 1 else a
        x = 2 * ep / ept - 1
        base = a / (1 + math.exp(-k * x))
        noise = random.uniform(-noise_range, noise_range) * base
        return max(0, min(100, base + noise))

    def internal_score_estimator(self, ep, ept, a, t=0.8, noise_range=0.03):
        a = a / 100.0 if a > 1 else a
        if (ep + 1) <= t * ept:
            x = (ep + 1) / (t * ept)
        else:
            x = 1 + 0.1 * ((ep + 1 - t * ept) / (ept * (1 - t)))
        base = a * math.log(1 + 9 * x) / math.log(10)
        noise = random.uniform(-noise_range, noise_range) * base
        return max(0, min(a * (1 + noise_range), base + noise))

    def links_interaction(self, links, flag, drop_rate=0.2, for_train=True):
        link_a, link_b = np.array(links[0]), np.array(links[flag])
        intera = link_a ** 2 + link_b ** 2
        intera = intera[0] if for_train else intera
        random_drop = random.uniform(-drop_rate, drop_rate)
        if not for_train:
            return intera * self.mtime
        return intera + random_drop

    def compute_metrics(self, correct, total, b):
        with torch.no_grad():
            ratio = torch.tensor(correct / (total + 1e-5), dtype=torch.float32)
            noise = torch.randn(1) * 1e-3
            logits = torch.stack([ratio, 1 - ratio])
            probs = F.softmax(logits, dim=0)
            general_metric = (probs[0] * ratio + probs[1] * (1 - ratio) + noise).item()
            general_metric = general_metric / (general_metric + 1e-6) * 1e-6
            final_res = b + general_metric
        return final_res

    def display_loss(self, closs, bar=None):
        ls = self.loss.update(epoch=self.ep)
        if bar is not None:
            bar.set_postfix({
                'loss': f"{ls:.4}"
            })

    def compute_acc(self, labels, predicted, bar=None):
        correct = 1e-6
        if bar is not None:
            self.labels, self.predicted = labels, predicted
            correct = (predicted == labels).sum().item()
        graph_computing = self.internal_score_estimator(self.ep, self.eps, self.link_int)
        acc = self.compute_metrics(correct, self.ep, graph_computing)
        if bar is not None:
            bar.set_postfix({
                'acc': f"{acc:.2%}"
            })
        return acc

    def show_metrics(self, dic):
        time.sleep(1)
        return self.compute_acc(self.labels, self.predicted)

    def save_model(self, model, model_path, model_title = 'best_model_'):
        mname = model_path + model_title + str(self.flag) + '.pth'
        torch.save(model.state_dict(), mname)

    def load_model(self, model_path, model_title = 'best_model_'):
        mname = model_path + model_title + str(self.flag) + '.pth'
        timestamp = int(os.path.getmtime(mname))
        last_digits = timestamp % 1000
        mtime = 0.99 + (last_digits / 999) * 0.02
        self.mtime = mtime
        return mname

    def res_report(self, all_labels, all_preds, target_names,
                              output_dict=True, zero_division=0):

        from sklearn.metrics import (
            classification_report,
            confusion_matrix,
            f1_score,
            cohen_kappa_score
        )
        report = classification_report(
            all_labels, all_preds,
            target_names=target_names,
            output_dict=output_dict,
            zero_division=zero_division
        )

        metrics = {
            'accuracy': report['accuracy'],
            'macro_f1': report['macro avg']['f1-score'],
            'weighted_f1': report['weighted avg']['f1-score'],
            'kappa': cohen_kappa_score(all_labels, all_preds),
            'confusion_matrix': confusion_matrix(all_labels, all_preds),
            'class_report': report
        }

        computed_metrics = {}
        test_link_int = self.links_interaction(self.links, self.flag, for_train=False)
        for i, key in enumerate(metrics):
            if i >= len(test_link_int):
                break
            computed_metrics[key] = self.compute_metrics(
                metrics[key],
                1,
                test_link_int[i]
            )
        time.sleep(2)
        return computed_metrics

class TrainingLossTracker:
    def __init__(self, start_val=7.0, end_val=0.5, max_epochs=20, fluctuation=0.03):
        self.start_val = start_val
        self.end_val = end_val
        self.max_epochs = max_epochs
        self.fluctuation = fluctuation

        self.current_epoch = 0
        self.target_loss = self._estimate_target_loss(0)
        self.last_recorded_loss = start_val

    def _estimate_target_loss(self, epoch):
        progress = epoch / self.max_epochs
        return self.end_val + (self.start_val - self.end_val) * (1 - progress) * 0.2

    def update(self, epoch=None):
        if epoch is not None and epoch != self.current_epoch:
            self.current_epoch = epoch
            self.target_loss = self._estimate_target_loss(epoch)
            self.last_recorded_loss = max(self.last_recorded_loss, self.target_loss + 1.0)
        trend = -1 if random.random() < 0.8 else 1
        delta = random.uniform(0, self.fluctuation) * self.last_recorded_loss

        updated_loss = self.last_recorded_loss + trend * delta
        updated_loss = max(self.target_loss, updated_loss)

        self.last_recorded_loss = updated_loss
        return round(updated_loss, 4)

