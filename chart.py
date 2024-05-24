import pandas as pd
import matplotlib.pyplot as plt

BACKGROUND_COLOR = (0, 0.025, 0.075)


def create_chart(date, csv_file):
    df = pd.read_csv(csv_file)
    df_sorted = df.sort_values(by=df.columns[-1], ascending=False)

    df_top10 = df_sorted.head(5)
    df_top10.set_index('Player', inplace=True)
    df_top10.T.plot(marker=',', markerfacecolor=BACKGROUND_COLOR, figsize=(10, 6), linewidth=0.6)

    plt.title('r/reddevils trends', fontsize=12, fontfamily='arial', pad=30, color='grey')
    plt.ylabel('Mentions', fontsize=9, color='grey')
    plt.legend(bbox_to_anchor=(1, 0.75), loc='upper left', edgecolor=BACKGROUND_COLOR,
               facecolor=BACKGROUND_COLOR, labelcolor='grey')

    plt.xticks(rotation=45, fontsize=9, color='grey')
    plt.yticks(fontsize=9, color='grey')
    plt.grid(True, alpha=0.2, color='grey')
    plt.grid(axis='x', color=BACKGROUND_COLOR)

    plt.gca().spines['top'].set_color(BACKGROUND_COLOR)
    plt.gca().spines['right'].set_color(BACKGROUND_COLOR)
    plt.gca().spines['bottom'].set_color('grey')
    plt.gca().spines['left'].set_color('grey')
    plt.gca().set_facecolor(BACKGROUND_COLOR)
    plt.gcf().set_facecolor(BACKGROUND_COLOR)

    plt.tight_layout()
    plt.savefig(f'{date}.png', bbox_inches='tight', dpi=600)
    plt.show()

    return f'{date}.png'
