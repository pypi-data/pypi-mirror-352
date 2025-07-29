
import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use("QtAgg")


def plot1_eps(w, epsd1e, epsd1, eps, eps1, eps2):
    # figure 1
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.semilogx(w, epsd1e, '-r', linewidth=2, label='electrolyte')
    ax.semilogx(w, epsd1, '-b', linewidth=2, label='suspension')
    ax.semilogx(w, eps, '--g', linewidth=2)
    ax.semilogx(w, eps1, '--b', linewidth=2)
    ax.semilogx(w, eps2, ':b', linewidth=2)

    ax.set_xlabel('rad/s')
    ax.set_ylabel('EPS')
    plt.title('including electrode polarization')
    ax.legend()
    ax.set_xlim(w[0], w[-1]+1)
    ax.set_ylim([60, 201])
    ax.yaxis.set_ticks(np.arange(60, 201, 20))    # plt.gca('LineWidth', 2, fontsize=12)
    plt.show()


def plot2_k(w, ktote, ktot, conduc):
    # figure 2
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.semilogx(w, ktote, '-r', linewidth=2, label='electrolyte')
    ax.semilogx(w, ktot, '-b', linewidth=2, label='suspension')
    ax.semilogx(w, conduc, '--g', linewidth=2)

    ax.set_xlabel('rad/s', fontsize=12)
    ax.set_ylabel('K', fontsize=12)
    plt.title('including/no electrode polarization')
    ax.legend()
    # ax[0].set_xlim(100, 1e6)
    # ax[0].set_ylim(60, 2e2)
    # plt.gca('LineWidth', 2, fontsize=12)
    # fig('Color', (1, 1, 1))
    plt.show()


def plot3(w, eps, eps1, eps2):
    # figure 3
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.loglog(w, eps, '-b', linewidth=2, label='electrolyte')
    ax.loglog(w, eps1, '--g', linewidth=2, label='suspension')
    ax.loglog(w, eps2, '--b', linewidth=2)

    ax.set_xlabel('rad/s', fontsize=12)
    ax.set_ylabel('EPS', fontsize=12)
    plt.title('no electrode polarization')
    ax.legend()
    # ax.set_xlim(100, 1e6)
    ax.set_ylim(60, 2e2)
    # plt.gca('LineWidth', 2, 'FontSize', 12)
    # fig('Color', (1, 1, 1))
    plt.show()
