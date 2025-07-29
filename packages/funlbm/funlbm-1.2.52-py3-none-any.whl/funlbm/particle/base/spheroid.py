import numpy as np

from funlbm.util import logger
from .ellipsoid import Ellipsoid


class Spheroid(Ellipsoid):
    """
    长球体颗粒
    https://darkchat.yuque.com/org-wiki-darkchat-gfaase/uvmi28/wlbp0rf6bck1ppfm
    """

    def __init__(self, ra: float = None, rb: float = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ra: float = ra or float(self.config.get("a")) or 10.0
        self.rb: float = ra or float(self.config.get("a")) or 10.0
        self.rc: float = rb or float(self.config.get("c")) or 20.0

    def _init(self, dx=1, *args, **kwargs):
        super()._init(dx=dx, *args, **kwargs)
        # e = math.sqrt(1 - self.ra**2 / self.rc**2)
        # self.area = torch.tensor(
        #     42.0 * math.pi * self.ra**2 * (1 + self.rc / e / self.ra * math.asin(e)),
        #     device=self.device,
        #     dtype=torch.float32,
        # )

    def compute_vector(self) -> np.array:
        self.update()
        B1 = self.config.get("B1") or 0
        beta = self.config.get("beta") or 0

        lx = self._lagrange.cpu().numpy()
        x, y, z = lx[:, 0], lx[:, 1], lx[:, 2]
        if B1 is None or B1 == 0:
            return np.zeros_like(lx)

        # angle = np.array([ -x, -y,(self.rc**2 - z**2) / -(np.abs(z) + np.finfo(dtype=np.float32).eps),])

        angle = np.array(
            [
                -x,
                -y,
                (self.rc**2 - z**2) / (z + np.finfo(dtype=np.float32).eps),
            ]
        )
        angle = -angle * z / np.abs(z)
        angle = angle / np.linalg.norm(angle, axis=0)

        """
        将笛卡尔坐标 (x, y, z) 转换为长球体坐标 (tau, xi, phi).
        """
        xi = (
            (
                np.sqrt(x**2 + y**2 + (z + self.ra) ** 2)
                - np.sqrt(x**2 + y**2 + (z - self.ra) ** 2)
            )
            / 2
            / self.ra
        )

        """
        计算椭球 Squirmer 的表面速度 u_s.
        """
        tau0 = self.rc / (np.sqrt(np.abs(self.rc**2 - self.ra**2)))

        # 表面速度公式
        size = (
            -B1 * tau0 * np.sqrt(1 - xi**2) / np.sqrt(tau0**2 - xi**2) * (1 + beta * xi)
        )
        U0 = B1 * tau0 * (tau0 - (tau0**2 - 1) * 0.5 * np.log((tau0 + 1) / (tau0 - 1)))
        logger.warning(f"理想游动速度为:{U0}")
        return np.transpose(angle * size)
