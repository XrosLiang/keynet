import numpy as np
import torch
import torchvision
from time import time
from torchvision import datasets, transforms
from torch import nn, optim
import torch.nn.functional as F


class LeNet(nn.Module):
    def __init__(self):
        super(LeNet, self).__init__()
        # 1 input image channel, 6 output channels, 3x3 square convolution
        # kernel
        self.conv1 = nn.Conv2d(1, 6, 3)
        self.conv2 = nn.Conv2d(6, 16, 3)
        # an affine operation: y = Wx + b
        self.fc1 = nn.Linear(16 * 6 * 6, 120)  # 6*6 from image dimension
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        # Max pooling over a (2, 2) window
        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))
        # If the size is a square you can only specify a single number
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)
        x = x.view(-1, self.num_flat_features(x))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features

    @staticmethod
    def transform():
        return transforms.Compose([transforms.Resize( (32,32) ),
                                   transforms.ToTensor(),                                    
                                   transforms.Normalize((0.1307,), (0.3081,))])


class Net(nn.Module):
    """https://github.com/pytorch/examples/blob/master/mnist/main.py"""
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4*4*50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

    @staticmethod
    def transform():
        return transforms.Compose([transforms.ToTensor(),                                    
                                   transforms.Normalize((0.1307,), (0.3081,))])


class Net_AvgPool(nn.Module):
    """https://github.com/pytorch/examples/blob/master/mnist/main.py"""
    def __init__(self):
        super(Net_AvgPool, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4*4*50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.avg_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.avg_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

    @staticmethod
    def transform():
        return transforms.Compose([transforms.ToTensor(),                                    
                                   transforms.Normalize((0.1307,), (0.3081,))])

def validate(net=Net(), mnistdir='/proj/enigma', modelfile='/proj/enigma/jebyrne/mnist.pth'):
    valset = datasets.MNIST(mnistdir, download=True, train=False, transform=net.transform())
    valloader = torch.utils.data.DataLoader(valset, batch_size=64, shuffle=True)

    net.load_state_dict(torch.load(modelfile))
    net.eval()

    (total, correct) = (0,0)
    for images,labels in valloader:
        for i in range(len(labels)):
            with torch.no_grad():
                output = net(images)

            _, pred = torch.max(output, 1)
            #pred = output.argmax(dim=1, keepdim=True) 
            total += labels.size(0)
            correct += (pred == labels).sum().item()

    print("Mean classification accuracy = %f" % (correct/total))


def train(net=Net(), mnistdir='/proj/enigma', modelfile='/proj/enigma/jebyrne/mnist.pth', lr=0.003, epochs=20):
    trainset = datasets.MNIST(mnistdir, download=True, train=True, transform=net.transform())
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)

    dataiter = iter(trainloader)
    #criterion = nn.CrossEntropyLoss()
    criterion = F.nll_loss
    optimizer = optim.SGD(net.parameters(), lr=lr, momentum=0.9)
    time0 = time()

    for e in range(epochs):
        running_loss = 0
        for images, labels in trainloader:
            optimizer.zero_grad()            
            output = net(images)
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()        
            running_loss += loss.item()
        else:
            print("Epoch {} - Training loss: {}".format(e, running_loss/len(trainloader)))

        print("Training Time (in minutes) =",(time()-time0)/60)

    torch.save(net.state_dict(), modelfile)


def avgpool():
    train(net=Net_AvgPool(), modelfile='/proj/enigma/jebyrne/mnist_avgpool.pth', lr=0.003, epochs=20)
    validate(net=Net_AvgPool(),  modelfile='/proj/enigma/jebyrne/mnist_avgpool.pth')

def maxpool():
    train(net=Net(), modelfile='/proj/enigma/jebyrne/mnist.pth', lr=0.003, epochs=20)
    validate(net=Net(),  modelfile='/proj/enigma/jebyrne/mnist.pth')

def lenet():
    train(net=LeNet(), modelfile='/proj/enigma/jebyrne/mnist_lenet.pth', lr=0.003, epochs=20)
    validate(net=LeNet(),  modelfile='/proj/enigma/jebyrne/mnist_lenet.pth')
