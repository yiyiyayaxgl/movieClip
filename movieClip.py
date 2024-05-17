import os
from moviepy.editor import VideoFileClip
from fpdf import FPDF
from PIL import Image

def get_image_size(image_path):
    with Image.open(image_path) as img:
        return img.size

def process_video(video_file, num_segments, pdf_dir):
    try:
        # 使用moviepy读取视频
        clip = VideoFileClip(video_file)

        # 计算每段视频的时长
        segment_duration = clip.duration / num_segments

        # 获取视频文件的目录
        video_dir = os.path.dirname(video_file)

        # 获取ClipTemp文件夹路径
        clip_temp_dir = os.path.join(video_dir, "ClipTemp")
        if not os.path.exists(clip_temp_dir):
            os.makedirs(clip_temp_dir)

        # 获取视频文件名（不包含扩展名）
        video_filename = os.path.splitext(os.path.basename(video_file))[0]

        # 分割并保存每段的开始帧为JPG图片
        frame_files = []  # 存储所有帧文件的路径
        for i in range(num_segments):
            start_time = i * segment_duration
            frame_filename = f"segment_{i + 1}.jpg"
            frame_path = os.path.join(clip_temp_dir, frame_filename)
            # 保存为JPG图片
            clip.save_frame(frame_path, t=start_time)
            frame_files.append(frame_path)

        # 使用PIL获取第一张图片的尺寸，假设所有图片尺寸相同
        first_frame_path = frame_files[0]
        width, height = get_image_size(first_frame_path)

        # 创建PDF对象，设置自定义页面尺寸
        pdf = FPDF(unit="pt", format=[width, height])
        for frame_path in frame_files:
            # 将JPG图片添加到PDF
            pdf.add_page()
            pdf.image(frame_path, 0, 0, width, height)

        # 保存PDF文件到指定目录或视频所在目录
        pdf_filename = f"{video_filename}.pdf"
        pdf_path = os.path.join(pdf_dir or video_dir, pdf_filename)
        pdf.output(pdf_path)

        # 删除ClipTemp文件夹及其内容
        for root, dirs, files in os.walk(clip_temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(clip_temp_dir)

        print(f"视频文件 {video_file} 的PDF保存成功")
    except Exception as e:
        print(f"处理视频文件 {video_file} 时出错: {e}")

def split_and_capture_frames(directory):
    video_extensions = ('avi', 'mkv', 'mov', 'wmv', 'mp4', 'ts')
    video_files = []
    # 遍历目录和子目录下的所有视频文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(video_extensions):
                video_files.append(os.path.join(root, file))

    num_videos = len(video_files)
    print(f"共找到 {num_videos} 个视频文件待处理.")

    # 询问用户是否需要指定PDF保存目录
    pdf_dir = input("输入需要保存PDF的目录（默认保存到视频所在目录，直接按回车跳过）: ")
    pdf_dir = pdf_dir.strip()  # 去除输入字符串两端的空白字符
    if pdf_dir and not os.path.isdir(pdf_dir):
        print(f"错误：{pdf_dir} 不是一个有效的目录.")
        return

    num_segments = int(input("输入要将视频分割成的片段数量 (10-1000): "))
    if not (10 <= num_segments <= 1000):
        print("片段数量必须在10到1000之间.")
        return

    for i, video_file in enumerate(video_files, start=1):
        print(f"正在处理 {video_file} - {i}/{num_videos} ({i / num_videos * 100:.2f}%)")
        process_video(video_file, num_segments, pdf_dir)

# 启动函数
if __name__ == "__main__":
    directory = input("输入包含视频文件的目录路径: ")
    if not os.path.isdir(directory):
        print(f"错误：{directory} 不是一个有效的目录.")
    else:
        split_and_capture_frames(directory)