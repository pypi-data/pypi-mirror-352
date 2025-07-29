from scipy.special import softmax as sm
import torch.utils
import torch.utils.data
from tqdm import tqdm
from zipfile import ZipFile
from urllib import request
import torch
import os
import time
import random
from torchvision.transforms import v2
import lightning as L
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import numpy as np
from torchvision.io import read_image, ImageReadMode
import matplotlib.pyplot as plt
import torch
from dataclasses import dataclass, field
from sklearn.model_selection import train_test_split
from typing import Union, Type, Callable
from torch.utils.data.sampler import WeightedRandomSampler
import torchvision.transforms as T
from PIL import Image

from ..utils.data_utils import min_max_norm, read_image_to_tensor_from_path
from ..utils.pytorch_utils import clear_memory
from ..utils import plotting_utils
from ..utils.module_utils import init_object
from .mix import *


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def remove(path):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Fire: {path} might be removed already")


def download(url, filename):
    if not os.path.exists(filename):
        print(f"Start downloading from: {url} to {filename}")
        with DownloadProgressBar(
            unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]
        ) as t:
            request.urlretrieve(url, filename=filename, reporthook=t.update_to)
    else:
        print(f"File exist: {filename}")


def download_and_extract(url, zip_filename, extract_dir):
    download(url, zip_filename)
    with ZipFile(zip_filename, "r") as zip_f:
        zip_f.extractall(extract_dir)
    remove(zip_filename)


def get_dataset_base(*dst):
    if os.environ.get("DATA_SET_BASE") is None:
        b = os.path.join(os.path.expanduser("~"), "autodl-tmp", "ml_data")
    else:
        b = os.environ.get("DATA_SET_BASE")
    base = os.path.join(b, *dst)
    if not os.path.exists(os.path.dirname(base)):
        os.makedirs(os.path.dirname(base), exist_ok=True)
    return base


def rand(r1, r2):
    return ((r1 - r2) * torch.rand(1) + r2).item()


tensor_tran = transforms.ToTensor()


def get_label_count_from_y(y):
    label_count = {}
    for label in y:
        if label_count.get(label) is None:
            label_count[label] = 0
        label_count[label] += 1
    return label_count


def print_label_count(label_count: dict):
    d = []
    for k, v in label_count.items():
        d.append([k, v])

    d = sorted(d, key=lambda kv: kv[1])
    for k, v in d:
        print(f"{k}: {v} ({round((v / np.sum(list(label_count.values()))) * 100, 2)}%)")


def print_label_count_from_y(y):
    print("Total size:", len(y))
    print_label_count(get_label_count_from_y(y))


def _to_tensor(x):
    if type(x) is torch.Tensor:
        return x
    else:
        return transforms.ToTensor()(x)


@dataclass(kw_only=True)
class MixAugSampler:

    num_classes: int

    class_weight: list[int] = None
    j_sampling_counting: list[int] = None
    label_count: dict = None
    j_sampling_strategy: str = "exclusive_and_uniform"
    weight_update_lr: float = 1e-1
    debug: bool = False

    def init(self, y):
        self.label_count = get_label_count_from_y(y)
        self.sample_count = np.bincount(y)
        if self.j_sampling_strategy in [
            "non_exclusive_and_distributedly_weighted",
            "non_exclusive_and_distributedly_weighted_and_reweight_by_performance",
            "non_exclusive_and_distributedly_weighted_and_reweight_by_performance_b",
        ]:
            self.class_weight_original = 1.0 / self.sample_count
            self.class_weight = np.copy(self.class_weight_original)
        if (
            self.j_sampling_strategy
            == "non_exclusive_and_log_freq_weighted_and_reweight_by_log_freq"
        ):
            self.class_weight = np.log(self.sample_count) / self.sample_count

        if (
            self.j_sampling_strategy
            == "non_exclusive_and_log_freq_weighted_and_reweight_by_sqrt_freq"
        ):
            self.class_weight = np.sqrt(self.sample_count) / self.sample_count

        self.sample_idx = [i for i in range(len(y))]

        self.label_exclusive_idx = {}
        for label_ in self.label_count.keys():
            self.label_exclusive_idx[label_] = np.argwhere(
                y != label_).flatten()

        self.j_sampling_counting = [0 for i in range(self.num_classes)]
        print("--- Init MixAugSampler:", self.j_sampling_strategy)
        print("---", self.sample_count, self.debug, self.weight_update_lr)

    def get_sample_idx(self, y, i_target):
        if self.j_sampling_strategy == "exclusive_and_uniform":
            j_idx = random.choice(self.label_exclusive_idx[i_target])
        elif self.j_sampling_strategy in [
            "non_exclusive_and_distributedly_weighted",
            "non_exclusive_and_distributedly_weighted_and_reweight_by_performance",
            "non_exclusive_and_distributedly_weighted_and_reweight_by_performance_b",
            "non_exclusive_and_log_freq_weighted_and_reweight_by_log_freq",
            "non_exclusive_and_log_freq_weighted_and_reweight_by_sqrt_freq",
        ]:
            j_idx = random.choices(
                self.sample_idx, self.class_weight[y], k=1)[0]
        else:
            j_idx = random.choice(self.sample_idx)

        return j_idx

    def get_j_sampling_counting(self):
        return self.j_sampling_counting

    def get_class_sampling_prob(self):
        return (
            self.class_weight * self.sample_count
            if self.class_weight is not None
            else [-1]
        )

    def update_class_weight(self, new_weight_loss):
        if self.debug:
            print("----- old prob ------")
            print(self.get_class_sampling_prob())
            print()
            print("----- new_weight_loss ------")
            print(new_weight_loss)
            print()
        if (
            self.j_sampling_strategy
            == "non_exclusive_and_distributedly_weighted_and_reweight_by_performance"
        ):
            self.class_weight = (
                self.get_class_sampling_prob()
                + (self.weight_update_lr * new_weight_loss)
            ) / self.sample_count
        elif (
            self.j_sampling_strategy
            == "non_exclusive_and_distributedly_weighted_and_reweight_by_performance_b"
        ):
            self.class_weight = new_weight_loss / self.sample_count
        if self.debug:
            print("----- new prob ------")
            print(self.get_class_sampling_prob())
            print()


@dataclass(kw_only=True, init=False)
class CommonDatasetAndDataModule:

    # default
    # deprecated attr
    sal_path_transfer_func: Callable[[str], str] = None

    num_classes: int = None
    head_classes_idx: tuple = None
    medium_classes_idx: tuple = None
    tail_classes_idx: tuple = None

    class_labels: tuple = None

    # transform: v2.Compose = field(default_factory=list)
    # target_transform: v2.Compose = None
    transform: list = field(default_factory=list)
    mixed_aug_with_target: Union[list | AugmentBase] = None
    mixed_aug_with_target_and_model: Union[list | AugmentBase] = None
    target_transform: list = None
    test_size: float = 0.2
    random_state: int = 42
    verbose: bool = False
    return_img_path: bool = False
    return_original: bool = False
    return_saliency: bool = False
    saliency_map_data_dir: list[str] = None
    saliency_erasing_kwargs: dict = field(default_factory=dict)

    class_balanced_sampling: bool = False

    j_sampling_strategy: str = "exclusive_and_uniform"
    mix_aug_sampler: MixAugSampler = None
    mix_aug_sampler_kwargs: dict = field(default_factory=dict)

    return_saliency_only: bool = False
    task_type: str = "multiclass"

    dataset_init_kwargs: dict = field(default_factory=dict)

    def get_head_classes_idx(self):
        return (
            np.array(self.head_classes_idx)
            if self.head_classes_idx is not None
            else None
        )

    def get_medium_classes_idx(self):
        return (
            np.array(self.medium_classes_idx)
            if self.medium_classes_idx is not None
            else None
        )

    def get_tail_classes_idx(self):
        return (
            np.array(self.tail_classes_idx)
            if self.tail_classes_idx is not None
            else None
        )


@dataclass(kw_only=True)
class XEraseDataset(Dataset, CommonDatasetAndDataModule):

    data_dir: list[str]
    is_train: bool = True
    # default
    download: bool = False
    __se__ = None

    def __check_if_downloaded__(self):
        """
        check dataset download
        """
        raise NotImplementedError()

    def __download_data__(self):
        """
        Prepare the data
        """
        raise NotImplementedError()

    def __check_if_saliency_map_downloaded__(self):
        """
        check dataset download
        """
        raise NotImplementedError()

    def __download_saliency_map_data__(self):
        """
        Prepare the data
        """
        raise NotImplementedError()

    def __x_y_pair_list__(self) -> np.ndarray | tuple:
        """
        return [[x1_path, y1], ..., [xn_path, yn]]
        """
        raise NotImplementedError()

    def __sal_path_transfer_full__(self, img_path) -> str:
        if self.saliency_map_data_dir is None:
            raise RuntimeError(
                "please define saliency_map_data_dir for data module")
        img_path = img_path.replace(self.data_dir, self.saliency_map_data_dir)

        # call dataset specific path transfer function
        return self.__sal_path_transfer__(img_path)

    def __sal_path_transfer__(self, img_path) -> str:
        """
        return [[x1_path, y1], ..., [xn_path, yn]]
        """
        raise NotImplementedError()

    def __get_x_path__(self, idx: str) -> str:
        """
        return file path of x
        """
        raise NotImplementedError()

    def __get_x__(self, idx: int) -> torch.Tensor:
        """
        return x
        """
        return self.__get_image_tensor_from_path__(self.__get_x_path__(idx))

    def __get_y__(self, idx: int) -> torch.Tensor:
        """
        the default get y, y should be numerical
        """
        if self.task_type == "multiclass":
            return int(self.y[idx])
        if self.task_type == "image-captioning":
            return self.y[idx]

    def __get_x_path__(self, idx: str) -> str:
        return self.x[idx]

    def __get_image_tensor_from_path__(
        self, img_path: str, mode=ImageReadMode.RGB
    ) -> torch.Tensor:
        return read_image_to_tensor_from_path(img_path, mode=mode)

    def __post_init__(self):
        if self.saliency_map_data_dir is not None:
            if len(self.saliency_map_data_dir) != len(self.data_dir):
                raise RuntimeError(
                    "saliency_map_data_dir and data_dir should have the same length"
                )
            self.saliency_map_data_dir = get_dataset_base(
                *self.saliency_map_data_dir)

        self.data_dir = get_dataset_base(*self.data_dir)

        if self.download:
            if not self.__check_if_downloaded__():
                print("Start download to: ", self.data_dir)
                os.makedirs(self.data_dir, exist_ok=True)
                self.__download_data__()
                print("Finished download dataset")
            else:
                print("Dataset exist: ", self.data_dir)

            if (
                self.saliency_map_data_dir is not None
                and not self.__check_if_saliency_map_downloaded__()
            ):
                print("Start download to: ", self.saliency_map_data_dir)
                os.makedirs(self.saliency_map_data_dir, exist_ok=True)
                self.__download_saliency_map_data__()
                print("Finished download saliency map dataset")
            else:
                print("Saliency Dataset exist: ", self.saliency_map_data_dir)

        x_y_pair = self.__x_y_pair_list__()

        # been split already in the __x_y_pair_list__
        if type(x_y_pair) is tuple:
            train_x_y_pair, test_x_y_pair = x_y_pair

            X_train = train_x_y_pair[:, 0]
            y_train = train_x_y_pair[:, 1]

            X_test = test_x_y_pair[:, 0]
            y_test = test_x_y_pair[:, 1]

        else:
            self.ox = x_y_pair[:, 0]
            self.oy = x_y_pair[:, 1]

            X_train, X_test, y_train, y_test = train_test_split(
                self.ox,
                self.oy,
                test_size=self.test_size,
                random_state=self.random_state,
            )

        if self.is_train:
            self.x = X_train
            self.y = y_train
        else:
            self.x = X_test
            self.y = y_test

        # transfer y into label in advance
        if self.task_type == "multiclass":
            num_y = [self.__get_y__(i) for i in range(len(self.y))]
            self.y = np.array(num_y)
        else:
            self.y = np.array(self.y)

        if self.task_type == "multiclass":
            self.label_count = get_label_count_from_y(self.y)
            self.class_weight_original = 1.0 / np.bincount(self.y)
            self.class_weight = np.copy(self.class_weight_original)
            self.sample_idx = np.array([i for i in range(len(self.y))])
            self.label_count_array = np.array(
                [self.label_count[i]
                    for i in range(len(self.label_count.keys()))]
            )

            self.label_exclusive_idx = {}
            for label_ in self.label_count.keys():
                self.label_exclusive_idx[label_] = np.argwhere(
                    self.y != label_).flatten()

            if self.class_balanced_sampling:
                # label should be numerical
                self.class_balanced_sampler = WeightedRandomSampler(
                    self.class_weight[self.y], len(self.y)
                )

        if self.verbose:
            print(
                "Train" if self.is_train else "Test",
                "set, size:",
                len(self.x),
            )

            # print_label_count(self.label_count)
            # print(self.label_count)
            def autolabel(rects):
                """
                Attach a text label above each bar displaying its height
                """
                for rect in rects:
                    height = rect.get_height()
                    ax.text(
                        rect.get_x() + rect.get_width() / 2.0,
                        1.02 * height,
                        # f"{round(height, 4)}\n ({round((height / len(self.x)) * 100, 2)}%)",
                        f"{round(height, 4)}",
                        ha="center",
                        va="bottom",
                    )

            if self.task_type == "multiclass":
                x_v = np.array([str(xx)
                                for xx in sorted(list(self.label_count.keys()))])
                y_v = np.array([self.label_count[int(xx)] for xx in x_v])
                sort_idx = np.argsort(y_v)
                x_v = x_v[sort_idx]
                y_v = y_v[sort_idx]

                if (
                    self.get_tail_classes_idx() is None
                    or len(self.get_tail_classes_idx().shape) == 0
                ):
                    print_label_count_from_y(self.y)
                else:
                    colors = ["pink" for i in range(
                        len(self.get_tail_classes_idx()))]
                    colors += ["red" for i in range(
                        len(self.get_medium_classes_idx()))]
                    colors += ["blue" for i in range(
                        len(self.get_head_classes_idx()))]
                    # fig, ax = plt.subplots(figsize=(20, 5), dpi=100)
                    # y_v = [self.label_count[int(xx)] for xx in x_v]
                    # rects = ax.bar(x_v, y_v, label=x_v, color=colors)
                    # autolabel(rects)

                    stras = ["original", "sqrt", "log"]

                    for stra in stras:
                        if hasattr(np, stra):
                            y_v = getattr(np, stra)(y_v)
                        fig, ax = plt.subplots(figsize=(20, 5), dpi=100)
                        rects = ax.bar(x_v, y_v, label=x_v, color=colors)
                        autolabel(rects)
                        plt.title(stra)
                        plt.show()

                if self.class_balanced_sampling:
                    print("Class-balanced sampling training enabled")

        if len(self.saliency_erasing_kwargs.keys()) > 0:
            if self.saliency_erasing_kwargs.get("blur_sigma") is None:
                raise RuntimeError(
                    "Please provide blur_sigma argument if saliency_erasing_kwargs is not empty."
                )
            else:
                self.__se__ = SaliencyErasing(
                    num_classes=self.num_classes, **self.saliency_erasing_kwargs
                )

        if type(self.transform) is list and len(self.transform) > 0:
            self.transform = v2.Compose(self.transform)

        if type(self.target_transform) is list:
            self.target_transform = v2.Compose(self.target_transform)

    def __len__(self):
        return len(self.x)

    def __split_transform__(self):
        return self.transform.transforms[0], v2.Compose(self.transform.transforms[1:])

    def __get_raw__(self, idx) -> Union[str, torch.Tensor, torch.Tensor]:
        img_path = self.__get_x_path__(idx)
        image = self.__get_x__(idx)
        target = self.y[idx]
        return image, target, img_path

    def make_demo_dataset(self, replaced):
        train_size = 50 / len(self.x)
        X_train, X_test, y_train, y_test = train_test_split(
            self.x,
            self.y,
            train_size=train_size,
            random_state=self.random_state,
        )
        topil = T.ToPILImage()

        for x in tqdm(X_train):
            img = self.transform(self.__get_image_tensor_from_path__(x))
            sal_path = self.__sal_path_transfer_full__(x)
            sa_img = self.__get_image_tensor_from_path__(sal_path)
            new_path = x.replace(replaced, f"{replaced}quick_demo/").replace(
                ".jpg", ".png"
            )
            new_sal_path = sal_path.replace(replaced, f"{replaced}quick_demo/")
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            os.makedirs(os.path.dirname(new_sal_path), exist_ok=True)
            topil(img).save(new_path)
            topil(sa_img).save(new_sal_path)

    def __getitem__(self, idx):
        result = []
        if self.return_saliency_only:
            img_path = self.__get_x_path__(idx)
            sal_path = self.__sal_path_transfer_full__(img_path)
            image = self.__get_image_tensor_from_path__(sal_path)
            target = self.y[idx]
            result = [self.transform(image), target]
        else:
            image, target, img_path = self.__get_raw__(idx)
            x_transform = self.transform
            # the first element should always be the image for training, it should be in aug or image
            if self.__se__ is not None and (torch.rand(1) < self.__se__.p):
                sal_path = self.__sal_path_transfer_full__(img_path)
                resize, x_transform = self.__split_transform__()
                image = resize(image)

                j_sample_idx = self.mix_aug_sampler.get_sample_idx(
                    self.y, target)
                j_image, j_target, j_img_path = self.__get_raw__(j_sample_idx)
                j_sal_path = self.__sal_path_transfer_full__(j_img_path)

                self.mix_aug_sampler.j_sampling_counting[self.y[j_sample_idx]] += 1

                j_image = resize(j_image)

                # __call__
                aug, target = self.__se__(
                    image, target, sal_path, j_image, j_target, j_sal_path
                )

                result.append(x_transform(
                    aug) if x_transform is not None else aug)
            else:
                result.append(x_transform(image)
                              if x_transform is not None else image)

            if (
                self.__se__ is not None
                and self.__se__.p > 0.0
                and len(target.shape) == 0
            ):
                new_target = np.zeros(self.num_classes, dtype=np.float32)
                new_target[target] = 1
                target = new_target

            # the second element should always be the target
            result.append(
                (
                    self.target_transform(target)
                    if self.target_transform is not None
                    else target
                )
            )

            # the third element should always be the target
            if self.return_img_path:
                result.append(img_path)

            if self.return_saliency:
                img_path = self.__get_x_path__(idx)
                sal_path = self.__sal_path_transfer_full__(img_path)
                sal_image = self.__get_image_tensor_from_path__(sal_path)
                sal_image = self.transform(sal_image)
                result.append(sal_image)

        return result


@dataclass(kw_only=True)
class NewBasicDataModule(L.LightningDataModule, CommonDatasetAndDataModule):

    dataset_class: Type[XEraseDataset]
    img_size: int = 256
    mean_t: list[float] = field(default_factory=lambda: [0.5, 0.5, 0.5])
    std_t: list[float] = field(default_factory=lambda: [0.225, 0.225, 0.225])

    batch_size: int = 64
    train_batch_size: int = None
    val_batch_size: int = None
    test_batch_size: int = None
    data_loader_kwargs: dict = None
    class_balanced_sampling: bool = False
    class_balanced_sampling_on_val: bool = False

    suppress_aug_info_print: bool = False
    shuffle_loader: bool = True
    shuffle_val_loader: bool = False
    normalize: bool = False

    def get_filterred_dataset_init_kwargs(self):
        filterred = {
            k: v
            for k, v in self.__dict__.items()
            if k in self.dataset_class.__dataclass_fields__.keys()
        }
        return filterred
        
    def prepare_data(self):
        self.dataset_class(
            download=True,
            **self.get_filterred_dataset_init_kwargs(),
        )

    def setup(self, stage: str):
        if (
            torch.backends.mps.is_available()
            or self.trainer is None
            or (self.trainer is not None and self.trainer.fast_dev_run)
        ):
            self.data_loader_kwargs["num_workers"] = 0
            self.data_loader_kwargs["persistent_workers"] = False
        elif (
            torch.cuda.is_available()
            and self.data_loader_kwargs.get("num_workers", 0) != 0
        ):
            self.data_loader_kwargs["persistent_workers"] = True
            
        filterred = self.get_filterred_dataset_init_kwargs()

        if stage in ["fit"]:
            self.train = self.dataset_class(is_train=True, **filterred)

        # filterred.pop("saliency_map_data_dir")
        filterred.pop("saliency_erasing_kwargs")

        self.val = self.dataset_class(is_train=False, **filterred)
        self.test = self.val

        if self.mixed_aug_with_target is not None:
            self.mixed_aug_with_target.setup_based_on_dataset(
                self.train, self.test)

        if self.mixed_aug_with_target_and_model is not None:
            self.mixed_aug_with_target_and_model.setup_based_on_dataset(
                self.train, self.test)

    def __post_init__(self):
        # init LightningDataModule
        L.LightningDataModule.__init__(self)

        self.num_classes = self.dataset_class.num_classes
        self.head_classes_idx = self.dataset_class.head_classes_idx
        self.medium_classes_idx = self.dataset_class.medium_classes_idx
        self.tail_classes_idx = self.dataset_class.tail_classes_idx
        self.class_labels = self.dataset_class.class_labels
        self.task_type = self.dataset_class.task_type

        self.train_batch_size = (
            self.train_batch_size
            if self.train_batch_size is not None
            else self.batch_size
        )
        self.val_batch_size = (
            self.val_batch_size if self.val_batch_size is not None else self.batch_size
        )
        self.test_batch_size = self.val_batch_size

        primary_tf = []
        if self.img_size != None:
            primary_tf.append(
                transforms.Resize(
                    size=(self.img_size, self.img_size), antialias=True)
            )

        if len(self.transform) > 0:
            initialized_transform = []
            for settings in self.transform:
                if type(settings) is dict:
                    it = init_object(
                        settings["class_path"], settings["init_args"])
                else:
                    it = settings
                initialized_transform.append(it)
            self.transform = initialized_transform
        if self.mixed_aug_with_target is not None:
            it = None
            if type(self.mixed_aug_with_target) in [list, tuple]:
                it = init_object(
                    self.mixed_aug_with_target[0], dict(
                        num_classes=self.num_classes, config=self.mixed_aug_with_target[1]
                    )
                )
            self.mixed_aug_with_target = it
        if self.mixed_aug_with_target_and_model is not None:
            it = None
            if type(self.mixed_aug_with_target_and_model) in [list, tuple]:
                it = init_object(
                    self.mixed_aug_with_target_and_model[0],
                    dict(
                        num_classes=self.num_classes,
                        config=self.mixed_aug_with_target_and_model[1]
                    )
                )
            self.mixed_aug_with_target_and_model = it

        final_tf = [
            transforms.Lambda(_to_tensor),
        ]
        if self.normalize:
            final_tf += [
                v2.Normalize(
                    mean=torch.tensor(self.mean_t),
                    std=torch.tensor(self.std_t),
                    inplace=True,
                ),
            ]

        self.transform = v2.Compose([*primary_tf, *self.transform, *final_tf])

        self.no_aug_transform = v2.Compose([*primary_tf, *final_tf])
        self.data_loader_kwargs = (
            self.data_loader_kwargs
            if self.data_loader_kwargs is not None
            else dict(
                num_workers=0,
            )
        )

        self.train = None
        self.val = None
        self.test = None

        if not self.suppress_aug_info_print:
            print(f"Applied transform for training: \r\n{self.transform}")
            if self.mixed_aug_with_target is not None:
                print(
                    f"Applied mixed_aug_with_target for training: \r\n{self.mixed_aug_with_target}")
            if self.mixed_aug_with_target_and_model is not None:
                print(
                    f"Applied mixed_aug_with_target_and_model for training: \r\n{self.mixed_aug_with_target_and_model}")
            print(
                f"Applied transform for validating: \r\n{self.no_aug_transform}")

        self.save_hyperparameters(ignore=["dataset_class", "transform"])

    def has_mixed_based_aug(self):
        return self.mixed_aug_with_target is not None or self.mixed_aug_with_target_and_model is not None

    def mixed_based_transform(self, _x, _y):
        if self.mixed_aug_with_target is not None:
            return self.mixed_aug_with_target(_x, _y)

        if self.mixed_aug_with_target_and_model is not None:
            return self.mixed_aug_with_target_and_model(
                _x, _y
            )

        raise NotImplementedError()

    def get_x_y_from_mixed_based_result(self, aug_result):
        if self.mixed_aug_with_target is not None:
            return self.mixed_aug_with_target.get_x_y(aug_result)

        if self.mixed_aug_with_target_and_model is not None:
            return self.mixed_aug_with_target_and_model.get_x_y(aug_result)

        raise NotImplementedError()

    def get_loss_from_mixed_based_result(self, output, aug_result, loss_fn):
        loss = None
        if self.mixed_aug_with_target is not None:
            loss = self.mixed_aug_with_target.get_loss(
                output, aug_result, loss_fn)

        if self.mixed_aug_with_target_and_model is not None:
            loss = self.mixed_aug_with_target_and_model.get_loss(
                output, aug_result, loss_fn)

        if loss is None:
            raise NotImplementedError()
        else:
            return loss

    def __dataset_preprocessing__(self, stage, dataset: XEraseDataset):
        if dataset.__se__ is not None:
            self.mix_aug_sampler = MixAugSampler(
                num_classes=self.num_classes,
                j_sampling_strategy=self.j_sampling_strategy,
                debug=self.trainer.fast_dev_run if self.trainer is not None else False,
                **self.mix_aug_sampler_kwargs,
            )
            self.mix_aug_sampler.init(dataset.y)

            # assign mix_aug_sampler to dataset object
            dataset.mix_aug_sampler = self.mix_aug_sampler

        return dataset

    def train_dataloader(self):
        sampler = (
            None
            if not self.class_balanced_sampling
            else self.train.class_balanced_sampler
        )
        # print("train dataloader sampler:", sampler != None)

        return DataLoader(
            self.__dataset_preprocessing__("train", self.train),
            batch_size=self.train_batch_size,
            shuffle=self.shuffle_loader if not self.class_balanced_sampling else False,
            sampler=sampler,
            **self.data_loader_kwargs,
        )

    def val_dataloader(self):
        sampler = (
            None
            if not self.class_balanced_sampling_on_val
            else self.val.class_balanced_sampler
        )
        # print("val dataloader sampler:", sampler != None)
        return DataLoader(
            self.__dataset_preprocessing__("validate", self.val),
            batch_size=self.val_batch_size,
            shuffle=self.shuffle_val_loader,
            sampler=sampler,
            **self.data_loader_kwargs,
        )

    def test_dataloader(self):
        return DataLoader(
            self.__dataset_preprocessing__("test", self.test),
            batch_size=self.test_batch_size,
            shuffle=False,
            **self.data_loader_kwargs,
        )

    def predict_dataloader(self):
        return self.test_dataloader()

    def teardown(self, stage: str):
        # Used to clean-up when the run is finished
        if stage in ["fit"]:
            del self.train
            del self.val
        if stage in ["validate"]:
            del self.val
        if stage in ["test", "predict"]:
            del self.test

        clear_memory()


def translate(settings, translated_seg):
    h, w = translated_seg.shape
    x_offset, x_direction, y_offset, y_direction = settings
    if y_direction > 0:
        b_y_move = [0, h - y_offset]
        a_y_move = [y_offset, h]
    else:
        a_y_move = [0, h - y_offset]
        b_y_move = [y_offset, h]

    if x_direction > 0:
        b_x_move = [0, w - x_offset]
        a_x_move = [x_offset, w]
    else:
        a_x_move = [0, w - x_offset]
        b_x_move = [x_offset, w]
    new_translated_seg = torch.zeros_like(translated_seg)
    new_translated_seg[b_y_move[0]: b_y_move[1], b_x_move[0]: b_x_move[1]] = (
        translated_seg[a_y_move[0]: a_y_move[1], a_x_move[0]: a_x_move[1]]
    )
    return new_translated_seg


def get_new_direction():
    return random.choice([0, 1]), random.choice([0, 1])


def get_cover_ratio(original_seg, current_seg):
    # st = time.time()
    # if self.debug_metric.get("tt2") is None:
    #     self.debug_metric["tt2"] = 0
    # overlapping = torch.where((original_seg == 1.0) | (current_seg == 1.0), 0.5, 0)
    # overlapping = torch.where((original_seg == 1.0) & (current_seg == 1.0), 1, overlapping)
    # overlapping_only = torch.where((original_seg == 1.0) & (current_seg == 1.0), 1, 0)
    overlapping = original_seg + current_seg
    overlapping_only = torch.where(overlapping > 1.5, 1, 0)
    cover_ratio = (overlapping_only.sum() / original_seg.sum()).item()
    # self.debug_metric["tt2"] += time.time() - st
    return overlapping, overlapping_only, cover_ratio


def get_mask(
    seg,
    translate_steps=[10, 10],
    cover_ratio_range=[0.1, 0.9],
    debug=False,
    max_tran=100,
):
    current_cover_ratio = 100
    x_direction, y_direction = get_new_direction()
    translated_seg = seg.clone()
    # st = time.time()
    if len(cover_ratio_range.shape) == 1:
        low = cover_ratio_range[0]
        high = cover_ratio_range[1]
    else:
        crr_idx = np.random.random_integers(0, cover_ratio_range.shape[0] - 1)
        low = cover_ratio_range[crr_idx][0]
        high = cover_ratio_range[crr_idx][1]

    pit = np.random.uniform(low, high=high)
    tmp_cover_ratio_range = [max(0, pit - 0.1), min(pit + 0.1, 1)]
    c = 0
    while (
        not tmp_cover_ratio_range[0] <= current_cover_ratio <= tmp_cover_ratio_range[1]
    ):
        if c > max_tran:
            break
        else:
            c += 1
        if len(translate_steps) == 4:
            x_step = np.random.randint(
                translate_steps[0], high=translate_steps[1])
            y_step = np.random.randint(
                translate_steps[2], high=translate_steps[3])
        else:
            assert len(translate_steps) == 2
            x_step = np.random.randint(0, high=translate_steps[0])
            y_step = np.random.randint(0, high=translate_steps[1])

        settings = (
            x_step,
            x_direction,
            y_step,
            y_direction,
        )
        new_translated_seg = translate(settings, translated_seg)
        overlapping, overlapping_only, new_cover_ratio = get_cover_ratio(
            seg, new_translated_seg
        )

        if tmp_cover_ratio_range[0] <= new_cover_ratio <= current_cover_ratio:
            # it's moving forward
            translated_seg = new_translated_seg
            current_cover_ratio = new_cover_ratio
        else:
            # it's moving beyound or backward
            # if self.debug:
            #     print("Shift too much, reset and start over")
            #     print("Current coverage:", new_cover_ratio)

            current_cover_ratio = 100
            x_direction, y_direction = get_new_direction()
            translated_seg = seg.clone()

        # if self.debug:
        #     print("Directions: x", settings[1], ", and y", settings[-1])
        #     print("Steps: x", settings[0], ", and y", settings[2])
        #     print(current_cover_ratio)
        #     plotting_utils.plot_hor(
        #         [
        #             seg,
        #             new_translated_seg,
        #             overlapping,
        #             overlapping_only,
        #         ]
        #     )

    # self.debug_metric["tran_time"] = f"{time.time() - st:.8f}"
    # self.debug_metric["tt"] = f"{self.debug_metric['tt']:.8f}"
    # self.debug_metric["tt2"] = f"{self.debug_metric['tt2']:.8f}"
    return (
        translated_seg,
        overlapping,
        overlapping_only,
        current_cover_ratio,
        tmp_cover_ratio_range,
    )


def get_xerase_target(
    i_target,
    j_target,
    i_sal_or_blur,
    j_sal_or_blur,
    current_cover_ratio,
    num_classes,
    overlapping_only=None,
    saliency_guided_y=True,
    debug=False,
    softmax=False,
):
    new_target = np.zeros(num_classes, dtype=np.float32)
    if i_target != j_target:
        new_target[i_target] = 1 - current_cover_ratio
        new_target[j_target] = current_cover_ratio

        if saliency_guided_y:
            if debug:
                print()
                print("================")
                print("Original coverage based target:")
                print(new_target)

            new_target = np.zeros(num_classes, dtype=np.float32)

            # sal = self.__get_image_tensor_from_path__(sal_path)
            b_left_oo = torch.where(overlapping_only == 0, i_sal_or_blur, 0)
            # how many saliency value is left for the original
            i_sa = b_left_oo.sum() / i_sal_or_blur.sum()

            # j_sal = self.__get_image_tensor_from_path__(j_sal_path)
            j_b_oo = torch.where(overlapping_only == 1, j_sal_or_blur, 0)
            # how many saliency value is pick from the j sample
            j_sa = j_b_oo.sum() / j_sal_or_blur.sum()

            # print(new_target)
            if softmax:
                arr = sm([i_sa.item(), j_sa.item()])
                new_target[i_target] = arr[0]
                new_target[j_target] = arr[1]
            else:
                new_target[i_target] = i_sa
                new_target[j_target] = j_sa
                if debug:
                    print("Saliency based target before norm:")
                    print(new_target)
                new_target = min_max_norm(new_target)

            if debug:
                print("New saliency based target:")
                print(new_target)
                print("Sum:", new_target.sum())
    else:
        # if j sample is the same as i sample
        new_target[i_target] = 1

    return new_target


class SaliencyErasing:

    def __init__(
        self,
        blur_sigma=None,
        p=0.5,
        num_classes=-1,
        mask_with_noise: bool = False,
        translate_steps=[10, 10],
        seg_quantile=0.7,
        cover_ratio_range=[0.1, 0.9],
        erase_setting_per_class: dict = None,
        return_only_intersection: bool = False,
        debug: bool = False,
        max_tran: int = 100,
        saliency_guided_y: bool = False,
        softmax: bool = False,
    ) -> None:

        self.blur_sigma = blur_sigma
        if self.blur_sigma is not None:
            self.blurrer = v2.GaussianBlur(
                2 * int(self.blur_sigma) + 1, sigma=self.blur_sigma
            )
        else:
            raise RuntimeError("Please provide blur_sigma argument.")

        self.p = p
        self.return_only_intersection = return_only_intersection
        self.num_classes = num_classes
        self.mask_with_noise = mask_with_noise
        self.translate_steps = translate_steps
        self.seg_quantile = seg_quantile
        self.cover_ratio_range = np.array(cover_ratio_range)

        self.erase_setting_per_class = erase_setting_per_class
        self.debug = debug
        self.debug_metric = {"tran_count": 0}
        self.max_tran = max_tran
        self.saliency_guided_y = saliency_guided_y
        self.softmax = softmax

        self.to_pil = T.ToPILImage()

    def __get_image_tensor_from_path__(
        self, img_path: str, mode=ImageReadMode.RGB
    ) -> torch.Tensor:
        # same as https://github.com/pytorch/vision/blob/bf01bab6125c5f1152e4f336b470399e52a8559d/torchvision/datasets/folder.py#L260
        # which is the default way of torchvision reading image
        return read_image(img_path, mode=mode).float() / 255.0

    def get_blurred(self, sal, sal_path):
        blurred_save_path = self.get_blurred_save_path_from_sal_path(sal_path)
        if os.path.exists(blurred_save_path):
            blurred = self.__get_image_tensor_from_path__(
                blurred_save_path, mode=ImageReadMode.GRAY
            )[0]
        else:
            if sal is None:
                sal = self.__get_image_tensor_from_path__(sal_path)
            blurred = self.blurrer(sal)[0]
            self.to_pil(blurred).save(blurred_save_path)
        return blurred

    def get_blurred_save_path_from_sal_path(self, sal_path):
        return sal_path + f".b{self.blur_sigma}.png"

    def get_seg_save_path_from_sal_path(self, sal_path):
        blurred_save_path = self.get_blurred_save_path_from_sal_path(sal_path)
        blurred_quantile_save_path = f"{blurred_save_path[:-4]}.q{self.seg_quantile}"
        return f"{blurred_quantile_save_path}.seg.png"

    def get_seg(self, sal_path):
        # st = time.time()
        seg_save_path = self.get_seg_save_path_from_sal_path(sal_path)
        if os.path.exists(seg_save_path):
            seg = self.__get_image_tensor_from_path__(
                seg_save_path, mode=ImageReadMode.GRAY
            )[0]
        else:
            sal = self.__get_image_tensor_from_path__(sal_path)
            blurred = self.get_blurred(sal, sal_path)
            q = torch.quantile(blurred, q=self.seg_quantile).item()
            seg = torch.where(blurred > q, 1, 0).float()
            self.to_pil(seg).save(seg_save_path)
        # self.debug_metric["seg_time"] = f"{time.time() - st:.8f}"
        return seg

    def __call__(self, image, target, sal_path, j_image, j_target, j_sal_path):
        seg = self.get_seg(sal_path)
        st = time.time()
        (
            translated_seg,
            overlapping,
            overlapping_only,
            current_cover_ratio,
            tmp_cover_ratio_range,
        ) = get_mask(
            seg,
            cover_ratio_range=self.cover_ratio_range,
            translate_steps=self.translate_steps,
            debug=self.debug,
            max_tran=self.max_tran,
        )
        aug = torch.where(overlapping_only == 1, j_image, image)
        result = aug
        new_target = get_xerase_target(
            target,
            j_target,
            self.get_blurred(None, sal_path),
            self.get_blurred(None, j_sal_path),
            current_cover_ratio=current_cover_ratio,
            num_classes=self.num_classes,
            overlapping_only=overlapping_only,
            saliency_guided_y=self.saliency_guided_y,
            debug=self.debug,
            softmax=self.softmax,
        )

        if self.debug:
            self.debug_metric["total_time"] = f"{time.time() - st:.8f}"
            sal = self.__get_image_tensor_from_path__(sal_path)
            j_sal = self.__get_image_tensor_from_path__(j_sal_path)

            blurred = self.get_blurred(sal, sal_path)
            j_blurred = self.get_blurred(j_sal, j_sal_path)

            # what is removed
            b_oo = torch.where(overlapping_only == 1, blurred, 0)
            # what is left
            b_left_oo = torch.where(overlapping_only == 0, blurred, 0)

            # what is add
            j_b_oo = torch.where(overlapping_only == 1, j_blurred, 0)

            # what is miss
            j_b_miss_oo = torch.where(overlapping_only == 0, j_blurred, 0)

            plotting_utils.plot_hor(
                [
                    image.permute(1, 2, 0),
                    j_image.permute(1, 2, 0),
                    # sal.permute(1, 2, 0),
                    # j_sal.permute(1, 2, 0),
                    blurred,
                    j_blurred,
                    b_oo,
                    b_left_oo,
                    j_b_oo,
                    j_b_miss_oo,
                    # blurred if blurred is not None else torch.zeros_like(sal[0]),
                    seg if seg is not None else torch.zeros_like(image[0][0]),
                    # (
                    #     translated_seg
                    #     if translated_seg is not None
                    #     else torch.zeros_like(image[0][0])
                    # ),
                    (
                        overlapping
                        if overlapping is not None
                        else torch.zeros_like(image[0][0])
                    ),
                    # (
                    #     overlapping_only
                    #     if overlapping_only is not None
                    #     else torch.zeros_like(image[0][0])
                    # ),
                    result.permute(1, 2, 0),
                ]
            )
            print("Target: ", target)
            print("Rand target: ", j_target)
            print("New target: ", new_target)
            print("Temp cover_ratio_range: ", tmp_cover_ratio_range)
            print("Current_cover_ratio: ", current_cover_ratio)
            print("Debug: ", self.debug_metric)
            self.debug_metric = {"tran_count": 0}
            print("================")
            print()
        return result, new_target
