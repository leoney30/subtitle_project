import asyncio
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import calplot
from bilibili_api import user, sync
from bilibili_api.utils.network import HEADERS


HEADERS["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# ================================================
# ================= 配置区域 =================

BASE_DIR = "code/bili_stats"
TARGET_UID = 492498900
START_YEAR = datetime.datetime(2023, 2, 1)
OUTPUT_FILENAME = "code/bili_stats/bili_headmap.png"
# ===========================================

def str_time_to_seconds(time_str):
    """将视频时长字符串转换为秒"""
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0

def format_duration(seconds):
    """将秒数格式化为英文 10h 5m 格式"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m"

async def fetch_data():
    """从 B站 API 获取数据"""
    print(f"Fetching data for UID: {TARGET_UID}...")
    u = user.User(TARGET_UID)

    start_dt = START_YEAR
    start_ts = start_dt.timestamp()

    data_list = []
    page = 1
    keep_searching = True

    while keep_searching:
        try:
            res = await u.get_videos(pn=page, ps=50)
            v_list = res['list']['vlist']
        except Exception as e:
            print(f"Stop fetching (Page {page}): {e}")
            break

        if not v_list:
            break

        print(f"Processing page {page}...")

        for v in v_list:
            created_ts = v['created']

            if created_ts < start_ts:
                keep_searching = False
                break

            dt = datetime.datetime.fromtimestamp(created_ts)
            seconds = str_time_to_seconds(v['length'])

            data_list.append({
                'date': dt.date(),
                'seconds': seconds,
                'count': 1
            })

        page += 1
        await asyncio.sleep(2)

    return data_list

def generate_heatmap(data_list):
    """生成带有年度时长对比柱状图的 GitHub 风格图表"""
    if not data_list:
        print("No data found, cannot plot.")
        return

    print("Processing data and generating chart...")

    # 1. 数据处理
    df = pd.DataFrame(data_list)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # 按天统计（用于热力图）
    daily_stats = df.resample('D').agg({
        'count': 'sum',
        'seconds': 'sum'
    })

    # 2. 准备年份数据（倒序：最新年份在前）
    years = sorted(daily_stats.index.year.unique(), reverse=True)
    n_years = len(years)

    # 计算每年的总时长（用于柱状图）
    yearly_hours = []
    yearly_labels = []

    for year in years:
        total_seconds = daily_stats[daily_stats.index.year == year]['seconds'].sum()
        yearly_hours.append(total_seconds / 3600) # 转换为小时
        yearly_labels.append(str(year))

    # 3. 设置布局
    # 我们需要 N+1 行，第一行给柱状图，后面 N 行给热力图
    # height_ratios 控制高度比例：柱状图占 2 份，每个热力图占 1 份
    height_ratios = [2] + [1] * n_years

    fig, axes = plt.subplots(
        nrows=n_years + 1,
        ncols=1,
        figsize=(16, 2 + 3 * n_years), # 动态调整总高度
        gridspec_kw={'height_ratios': height_ratios, 'hspace': 0.4} # hspace增加子图间距
    )

    # 确保 axes 是列表（即使用户只有1年的数据）
    if n_years == 0: # 理论上不会发生，前面有 check
        return
    if n_years + 1 == 1: # 这句也是防御性编程
        axes = [axes]

    # ================= 绘制顶部柱状图 (Axes[0]) =================
    ax_bar = axes[0]

    # 绘制横向柱状图 (barh)
    # color='#40c463' 是 GitHub 贡献图的一种绿色
    bars = ax_bar.barh(yearly_labels, yearly_hours, color='#74ACDF', height=0.6)

    # 设置柱状图样式
    ax_bar.set_title("Total Duration by Year (Hours)", fontsize=16, fontweight='bold', pad=15)
    ax_bar.set_xlabel("", fontsize=12)
    ax_bar.invert_yaxis() # 关键：反转Y轴，让列表第一个（也就是最新年份）显示在最上面

    # 移除多余的边框，更美观
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    ax_bar.spines['left'].set_visible(False)

    # 在柱子旁边标注具体数值
    for bar in bars:
        width = bar.get_width()
        ax_bar.text(
            width + (max(yearly_hours) * 0.01), # x轴位置：柱子末端往右一点点
            bar.get_y() + bar.get_height()/2,   # y轴位置：柱子中间
            f'{width:.1f}h',                    # 文本内容
            va='center',
            fontsize=12,
            color='black'
        )

    # ================= 绘制年度热力图 (Axes[1:]) =================
    # 遍历剩下的 axes 和年份
    for i, year in enumerate(years):
        ax = axes[i + 1] # 跳过第0个（因为是柱状图）

        # 筛选数据
        year_data = daily_stats[daily_stats.index.year == year]['count']
        total_count = int(year_data.sum())
        total_seconds = daily_stats[daily_stats.index.year == year]['seconds'].sum()

        # 生成标题
        title_str = f"{year} | Videos: {total_count} | Duration: {format_duration(total_seconds)}"

        # 绘制热力图
        calplot.yearplot(
            year_data,
            year=year,
            ax=ax,
            cmap='Blues',
            linewidth=1.5,
            vmin=0,        # 0个视频对应最浅色
            vmax=3         # 超过或等于3个视频对应最深色 (增加颜色的对比度)
        )

        # 样式调整
        ax.set_title(title_str, fontsize=14, fontweight='bold', loc='center')
        ax.set_ylabel(str(year), color='black', fontsize=12, rotation=0, labelpad=20)

    # 4. 保存
    # plt.tight_layout() # 由于使用了 gridspec 和手动调整，有时候 tight_layout 会冲突，这里根据需要调整
    plt.savefig(OUTPUT_FILENAME, bbox_inches='tight', dpi=300)
    print(f"\nSuccess! Chart saved as: {OUTPUT_FILENAME}")

async def main():
    data = await fetch_data()
    generate_heatmap(data)

if __name__ == '__main__':
    sync(main())
