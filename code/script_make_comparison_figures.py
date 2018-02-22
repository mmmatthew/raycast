from default_settings import all as s
import os
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, auc
import pandas as pd
import seaborn as sns

sns.set(color_codes=True)
from itertools import compress

classifier_names = ["Nearest Neighbors",
                    "Linear SVM",
                    "RBF SVM",
                    # "Gaussian Process",
                    "Decision Tree",
                    "Random Forest",
                    "Neural Net",
                    "AdaBoost",
                    "Naive Bayes",
                    "QDA",
                    "LogisticRegression"]

iteration_name = '2018-01-25 17.43.50'


def main():
    multi_view_results_dir_root = os.path.join(
        s['general']['working_directory'],
        s['general']['iterations_subdir'],
        iteration_name,
        s['general']['iterations_structure']['fit'])

    single_view_results_dir_root = os.path.join(
        s['general']['working_directory'],
        s['general']['iterations_subdir'],
        iteration_name,
        s['general']['iterations_structure']['ortho_fit'])

    for classifier in classifier_names:
        if (os.path.exists(os.path.join(multi_view_results_dir_root, classifier)) &
                os.path.exists(os.path.join(single_view_results_dir_root, classifier))):

            f, ax = initialize_plot(classifier)

            # loop through folds and load data
            for fold_i in range(s['general']['do_folds']):
                file_multi_view = os.path.join(multi_view_results_dir_root, classifier,
                                               '3dclusters_test_{}.csv'.format(fold_i))
                file_single_view = os.path.join(single_view_results_dir_root, classifier,
                                                '3dclusters_test_{}.csv'.format(fold_i))

                # load data
                data_multi = pd.read_csv(file_multi_view)
                data_single = pd.read_csv(file_single_view)
                y_real_multi = data_multi.matched
                y_real_single = data_single.matched
                y_predicted_multi = data_multi.rating
                y_predicted_single = data_single.rating

                # update plot
                update_plot(ax, y_real_multi, y_real_single, y_predicted_multi, y_predicted_single)

            plot_filename = os.path.join(
                s['general']['working_directory'],
                'iterations',
                iteration_name, 'plots',
                'prc_{}.png'.format(classifier))
            finalize_plot(f, ax, plot_filename)

            # Create boxplot
            boxplot(ax, classifier)


def boxplot(data, classifier_name):
    single = pd.DataFrame({
        'real': data.y_real_single,
        'pred': data.y_predicted_single
    })
    single['true'] = single.pred[single.real]
    single['false'] = single.pred[~single.real]
    multi = pd.DataFrame({
        'real': data.y_real_multi,
        'pred': data.y_predicted_multi
    })
    multi['true'] = multi.pred[multi.real]
    multi['false'] = multi.pred[~multi.real]

    labels = ['true positives', 'false positives']
    f, ax = plt.subplots(1, 2, figsize=(5, 5), sharey=True)
    # ax[0].set_xlabel('Recall')
    ax[0].set_ylabel('Prediction')
    ax[0].set_ylim(0, 1)
    ax[0].set_title('Single-view')
    ax[1].set_title('Multi-view')
    ax[0].violinplot([list(single.true),
                      list(single.false)],
                     # notch=True,  # notch shape
                     # vert=True,  # vertical box alignment
                     # patch_artist=True,  # fill with color
                     )  # will be used to label x-ticks
    ax[1].violinplot([list(multi.true),
                      list(multi.false)],
                     # notch=True,  # notch shape
                     # vert=True,  # vertical box alignment
                     # patch_artist=True,  # fill with color
                     )  # will be used to label x-ticks
    ax[0].set_xticklabels(labels)
    ax[1].set_xticklabels(labels)
    plot_file = os.path.join(
        s['general']['working_directory'],
        'iterations',
        iteration_name, 'plots',
        'boxplot_{}.png'.format(classifier_name))
    f.tight_layout()
    f.savefig(plot_file)


def initialize_plot(classifier_name):
    f, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(classifier_name)
    ax.y_real_multi, ax.y_predicted_multi, ax.y_real_single, ax.y_predicted_single = [], [], [], []
    return f, ax


def update_plot(ax, y_real_multi, y_real_single, y_predicted_multi, y_predicted_single):
    # Multiview
    precision, recall, _ = precision_recall_curve(y_real_multi, y_predicted_multi)
    ax.plot(recall[recall < 1], precision[recall < 1], linestyle='-', color='#ffaaaa')
    # update list containing results from all folds
    ax.y_real_multi += list(y_real_multi)
    ax.y_predicted_multi += list(y_predicted_multi)

    # Singleview
    precision, recall, _ = precision_recall_curve(y_real_single, y_predicted_single)
    ax.plot(recall[recall < 1], precision[recall < 1], linestyle=':', color='#afafaf')
    # update list containing results from all folds
    ax.y_real_single += list(y_real_single)
    ax.y_predicted_single += list(y_predicted_single)
    return ax


def finalize_plot(f, ax, plot_file):
    precision, recall, _ = precision_recall_curve(ax.y_real_multi, ax.y_predicted_multi)
    lab = 'Multi-view AUC: %.4f' % (auc(recall, precision))
    ax.plot(recall[recall < 1], precision[recall < 1], label=lab, lw=2, color='#ff0000')
    precision, recall, _ = precision_recall_curve(ax.y_real_single, ax.y_predicted_single)
    lab = 'Single-view AUC: %.4f' % (auc(recall, precision))
    ax.plot(recall[recall < 1], precision[recall < 1], label=lab, lw=2, linestyle=':', color='#000000')
    ax.legend(loc='lower left', fontsize='small')
    f.tight_layout()
    f.savefig(plot_file)
    # plt.show()


main()
