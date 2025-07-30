import os
from pathlib import Path

import numpy as np
import tifffile as tf
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .data_loader_probability import PredictCellDataFile


class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(
                in_ch, out_ch, 3, padding=1
            ),  # in_ch、out_ch are number of channels
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.conv(x)


class UNet(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(UNet, self).__init__()
        self.conv1 = DoubleConv(in_ch, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = DoubleConv(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.conv3 = DoubleConv(128, 256)
        self.pool3 = nn.MaxPool2d(2)
        self.conv4 = DoubleConv(256, 512)
        self.pool4 = nn.MaxPool2d(2)
        self.conv5 = DoubleConv(512, 1024)
        # transposed convolution
        self.up6 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.conv6 = DoubleConv(1024, 512)
        self.up7 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.conv7 = DoubleConv(512, 256)
        self.up8 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.conv8 = DoubleConv(256, 128)
        self.up9 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.conv9 = DoubleConv(128, 64)

        self.conv10 = nn.Conv2d(64, out_ch, 1)  # kernel number

    def forward(self, x):
        c1 = self.conv1(x)  # convolution
        p1 = self.pool1(c1)  # downsampling
        c2 = self.conv2(p1)
        p2 = self.pool2(c2)
        c3 = self.conv3(p2)
        p3 = self.pool3(c3)
        c4 = self.conv4(p3)
        p4 = self.pool4(c4)

        c5 = self.conv5(p4)
        up_6 = self.up6(c5)  # upsampling
        merge6 = torch.cat([up_6, c4], dim=1)
        c6 = self.conv6(merge6)
        up_7 = self.up7(c6)
        merge7 = torch.cat([up_7, c3], dim=1)
        c7 = self.conv7(merge7)
        up_8 = self.up8(c7)
        merge8 = torch.cat([up_8, c2], dim=1)
        c8 = self.conv8(merge8)
        up_9 = self.up9(c8)
        merge9 = torch.cat([up_9, c1], dim=1)
        c9 = self.conv9(merge9)
        c10 = self.conv10(c9)

        out = nn.Sigmoid()(c10)  # to (0-1)
        return out


# Dice XMBD model prediction
def predict(INPUT_CNN_ARGS):
    """
    This function, reads the Dice-XMBD model:

    Weight = 02-15-20-14_threshold-99.7_withAugnoise-0.5_model_80),

    together a 512x512 Two-channel IMC image cube
    (16bit; channel#1: Nuclear; Channel#2: Cytoplasm)
    and returns a 3 channel-image data cube associated
    with the estimated probability map
    (512x512; 16bit; nuclear, cyto, background).

    Note: The functions is modified, from its original version,
    by Ali Dariush (26-April-2022)
    as part of an effort to develope an IMC pieline.

    input image array: 32-bit

    """
    model = UNet(
        INPUT_CNN_ARGS["n_input_channel"], INPUT_CNN_ARGS["n_input_channel"]
    )
    model.load_state_dict(
        torch.load(INPUT_CNN_ARGS["weight"], map_location="cpu")
    )
    # altered to only read in one tile
    image_name = str(
        Path(INPUT_CNN_ARGS["path_in"], INPUT_CNN_ARGS["file_ext_current"])
    )
    cell_dataset = PredictCellDataFile(
        image_file=image_name,
        threshold=INPUT_CNN_ARGS["th"],
        resize_crop=False,
        transform=None,
    )
    dataloaders = DataLoader(cell_dataset)
    model.eval()

    with torch.no_grad():
        for x in dataloaders:

            x = x.to(torch.float32)
            y = model(x)

            img_y = torch.squeeze(y).numpy()
            prob = ((2**16 - 1) * img_y).transpose(1, 2, 0)
            prob = prob.astype(np.uint16)

            tf.imwrite(
                os.path.join(
                    INPUT_CNN_ARGS["path_out"], INPUT_CNN_ARGS["file_ext_new"]
                ),
                prob,
            )
                prob,
            )
