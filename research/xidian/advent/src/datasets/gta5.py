# Copyright 2023 Xidian University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

import numpy as np

from src.datasets.base_dataset import BaseDataset


class GTA5DataSet(BaseDataset):
    def __init__(self, root, list_path, set='all',
                 max_iters=None, crop_size=(321, 321), mean=(128, 128, 128)):
        super().__init__(root, list_path, set, max_iters, crop_size, None, mean)

        # map to cityscape's ids
        self.id_to_trainid = {7: 0, 8: 1, 11: 2, 12: 3, 13: 4, 17: 5,
                              19: 6, 20: 7, 21: 8, 22: 9, 23: 10, 24: 11, 25: 12,
                              26: 13, 27: 14, 28: 15, 31: 16, 32: 17, 33: 18}

    def get_metadata(self, name):
        img_file = self.root / 'images' / name
        label_file = self.root / 'labels' / name
        return img_file, label_file

    def __getitem__(self, index):
        img_file, label_file, name = self.files[index]
        image = self.get_image(img_file)
        label = self.get_labels(label_file)
        # re-assign labels to match the format of Cityscapes
        label_copy = 255 * np.ones(label.shape, dtype=np.float32)
        for k, v in self.id_to_trainid.items():
            label_copy[label == k] = v
        image = self.preprocess(image)
        return image.copy().astype(np.float32), label_copy.copy().astype(np.int32)


if __name__ == '__main__':
    import mindspore.dataset as ds

    test_dataset = GTA5DataSet(root='./data/GTA5',
                                     list_path=f'./dataset/gta5_list/all.txt',
                                     set='all',
                                     crop_size=(1024,512),
                                     mean=np.array((104.00698793, 116.66876762, 122.67891434), dtype=np.float32),
                                     )

    test_loader = ds.GeneratorDataset(test_dataset, ["image", "label"], shuffle=False)
    test_loader = test_loader.batch(4)

    for data in test_loader.create_dict_iterator():
        image = data['image']
        label = data['label']
        print(np.unique(label.asnumpy()))