import copy
import os
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
from tqdm import trange
import flgo.algorithm.fedbase as fab
from torch.optim import lr_scheduler
import flgo.algorithm.fedavg as fedavg
import flgo.utils.fmodule as fuf
from torch.utils.data import Dataset
from torchvision.transforms import RandomCrop, RandomHorizontalFlip
import torchvision
import torch
import utils.submodule as usub
from utils.pdmodule import *
MIN_RATIO = 0.0625
class Server(fab.BasicServer):
    def initialize(self, *args, **kwargs):
        self.init_local_model()

    def init_local_model(self):
        def get_model_size(model):
            return sum(p.numel() for p in model.parameters()) * 4 / (1024 ** 2)
        total_size = get_model_size(self.model)
        all_p = np.arange(MIN_RATIO, 1.001, MIN_RATIO)
        size_ratio = [1.0*get_model_size(self.model.__class__(p))/total_size for p in all_p]
        for c in self.clients:
            pidx = 0
            while pidx+1 < len(all_p) and (size_ratio[pidx+1] <= c._capacity): pidx += 1
            c.p = all_p[pidx]
            c.model = self.model.__class__(c.p)

    def run(self):
        tune_key, tune_direction = self.gv.logger.get_es_key(), self.gv.logger.get_es_direction()
        tune_key = tune_key.split('_')[-1]
        for c in self.clients: c.tune_key, c.tune_direction = tune_key, tune_direction
        self.gv.logger.time_start('Total Time Cost')
        # evaluating initial model performance
        self.gv.logger.info("--------------Initial Evaluation--------------")
        self.gv.logger.time_start('Eval Time Cost')
        self.gv.logger.log_once()
        self.gv.logger.time_end('Eval Time Cost')
        # Standalone Training
        for c in self.clients: c.finetune()
        self.gv.logger.info("=================End==================")
        self.gv.logger.time_end('Total Time Cost')
        self.gv.logger.time_start('Eval Time Cost')
        self.gv.logger.log_once()
        self.gv.logger.time_end('Eval Time Cost')
        # save results as .json file
        self.gv.logger.save_output_as_json()
        return

class Client(fab.BasicClient):
    def finetune(self):
        dataloader = self.calculator.get_dataloader(self.train_data, batch_size=self.batch_size)
        self.model.to(self.device)
        optimizer = self.calculator.get_optimizer(self.model, lr=self.learning_rate, weight_decay=self.weight_decay, momentum=self.momentum)
        epoch_iter = trange(self.num_epochs+1)
        op_model_dict = copy.deepcopy(self.model.state_dict())
        op_met = self.test(self.model, 'val')
        # op_met = {'_'.join(['local', 'val', k] if self.tune_key.startswith('local') else ['val', k]): v for k,v in op_met.items()}
        op_epoch = 0
        for e in epoch_iter:
            if e<self.num_epochs:
                for batch_id, batch_data in enumerate(dataloader):
                    optimizer.zero_grad()
                    batch_data = self.calculator.to_device(batch_data)
                    loss = self.calculator.compute_loss(self.model, batch_data)['loss']
                    loss.backward()
                    if self.clip_grad > 0: torch.nn.utils.clip_grad_norm_(parameters=self.model.parameters(), max_norm=self.clip_grad)
                    optimizer.step()
                val_metric = self.test(self.model, 'val')
                # val_metric = {'_'.join(['local', 'val', k] if self.tune_key.startswith('local') else ['val', k]): v for k, v in val_metric.items()}
                if val_metric[self.tune_key]*self.tune_direction>op_met[self.tune_key]:
                    op_met = val_metric
                    op_epoch = e+1
                    op_model_dict = copy.deepcopy(self.model.state_dict())
                else:
                    if self.option['early_stop']>0 and (e+1 - op_epoch>=self.option['early_stop']):
                        epoch_iter.set_description("\t".join(["Client {}".format(self.id), "Optimal Epoch {}/{}".format(op_epoch, self.num_epochs)]+['{}: {:.4f}'.format(k, v) for k, v in op_met.items()]))
                        self.model.load_state_dict(op_model_dict)
                        break
                epoch_iter.set_description("\t".join(["Client {}".format(self.id), "Epoch {}/{}".format(e+1, self.num_epochs)] + ['{}: {:.4f}'.format(k,v) for k,v in val_metric.items()]))
            else:
                epoch_iter.set_description("\t".join(["Client {}".format(self.id), "Optimal Epoch {}/{}".format(op_epoch, self.num_epochs)] + ['{}: {:.4f}'.format(k, v) for k, v in op_met.items()]))
                self.model.load_state_dict(op_model_dict)
        return
