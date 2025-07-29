from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

# ccmap = getattr(cm, 'hot')
# ccmap = getattr(cm, 'CMRmap')
ccmap = getattr(cm, "turbo")
# ccmap = getattr(cm, 'jet')


def set_ccmap(k):
    global ccmap
    ccmap = getattr(cm, k)


# ANCHOR: Plotting
def_su_arg = dict(
    # rstride=1,
    # cstride=1,
    linewidth=1,
    antialiased=False,
    shade=False,
)


def clp(img):
    return np.clip(
        # np.transpose(img, (1, 2, 0)) * np.array([0.229, 0.224, 0.225])
        # + np.array([0.485, 0.456, 0.406]),
        np.transpose(img, (1, 2, 0)),
        0,
        1,
    )


def plot_hor(
    img_arrs,
    cmap=ccmap,
    solo=False,
    rows=None,
    columns=None,
    subplot_titles=None,
    idx=[],
    cb=False,
    save_path=None,
    show=True,
):
    if isinstance(cmap, str) and hasattr(cm, cmap):
        cmap = getattr(cm, cmap)
    size = 4
    # elif rows is not None and rows > 1 and columns is not None:
    if rows is not None and rows >= 1 and columns is not None:
        fig, axs = plt.subplots(
            rows,
            columns,
            figsize=(size * columns, size * rows),
        )
        for i in range(rows):
            for j in range(columns):
                if columns == 1:
                    axss = axs[i]
                elif rows == 1:
                    axss = axs[j]
                else:
                    axss = axs[i][j]
                plt.sca(axss)
                if subplot_titles is not None and i == 0:
                    # axs[i][j].title.set_text(subplot_titles[j], size=16)
                    axss.set_title(subplot_titles[j], fontsize=20)

                if j == 0:
                    axss.set_title(idx[i], fontsize=20)

                axss.axis("off")
                im = axss.imshow(img_arrs[i][j], cmap=cmap)
    else:
        if len(img_arrs) == 1:
            plt.figure(figsize=(size * len(img_arrs), size))
            plt.axis("off")
            im = plt.imshow(img_arrs[0], cmap=cmap)
        else:
            fig, axs = plt.subplots(
                1,
                len(img_arrs),
                figsize=(size * len(img_arrs), size),
            )
            for i in range(len(img_arrs)):
                plt.sca(axs[i])
                if subplot_titles is not None:
                    axs[i].set_title(subplot_titles[i], fontsize=20)
                axs[i].axis("off")
                im = axs[i].imshow(img_arrs[i], cmap=cmap)
    plt.tight_layout()
    if cb:
        plt.colorbar(im, ax=axs.ravel().tolist(), shrink=0.8)
    if save_path is not None:
        plt.savefig(save_path)
    if show:
        plt.show()
