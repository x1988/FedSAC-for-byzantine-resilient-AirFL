import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset, ConcatDataset

class DatasetSplit(Dataset):
    def __init__(self, dataset, idxs):
        self.dataset = dataset
        self.idxs = list(idxs)

    def __len__(self):
        return len(self.idxs)

    def __getitem__(self, item):
        image, label = self.dataset[self.idxs[item]]
        return image, label
    

def test_img(net_g, datatest, args):
    net_g.eval()
    
    # testing
    test_loss = 0
    correct = 0
    data_loader = DataLoader(datatest, batch_size=args.bs)
    #l = len(data_loader)
    with torch.no_grad():
        for idx, (data, target) in enumerate(data_loader):
            if args.gpu != -1:
                data, target = data.to(args.device), target.to(args.device)
            log_probs = net_g(data)
            # sum up batch loss
            test_loss += F.cross_entropy(log_probs, target, reduction='sum').item()
            
            # get the index of the max log-probability
            y_pred = log_probs.data.max(1, keepdim=True)[1]
            correct += y_pred.eq(target.data.view_as(y_pred)).long().cpu().sum()

        test_loss /= len(data_loader.dataset)
        accuracy = 100.00 * correct / len(data_loader.dataset)
    
        if args.verbose:
            print('\nTest set: Average loss: {:.4f} \nAccuracy: {}/{} ({:.2f}%)\n'.format(
                test_loss, correct, len(data_loader.dataset), accuracy))
        return accuracy, test_loss

def test_ind_img(net_g, datatest, args, idxs):
    net_g.eval()
    
    # testing
    test_loss = 0
    correct = 0
    data_loader = DataLoader(DatasetSplit(datatest, idxs), batch_size=1000)
    #l = len(data_loader)
    with torch.no_grad():
        for idx, (data, target) in enumerate(data_loader):
            if args.gpu != -1:
                data, target = data.to(args.device), target.to(args.device)
            log_probs = net_g(data)
            # sum up batch loss
            test_loss += F.cross_entropy(log_probs, target, reduction='sum').item()
            
            # get the index of the max log-probability
            y_pred = log_probs.data.max(1, keepdim=True)[1]
            correct += y_pred.eq(target.data.view_as(y_pred)).long().cpu().sum()

        accuracy = 100.00 * correct / len(data_loader.dataset)
        return accuracy