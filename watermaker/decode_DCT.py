from tkinter import filedialog, Tk, Button, Label, Text, WORD
from PIL import Image, ImageTk
import cv2
import numpy as np
import itertools
import time

# bảng lượng tử ưu tiên độ chói hình ảnh
quant = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                  [12, 12, 14, 19, 26, 58, 60, 55],
                  [14, 13, 16, 24, 40, 57, 69, 56],
                  [14, 17, 22, 29, 51, 87, 80, 62],
                  [18, 22, 37, 56, 68, 109, 103, 77],
                  [24, 35, 55, 64, 81, 104, 113, 92],
                  [49, 64, 78, 87, 103, 121, 120, 101],
                  [72, 92, 95, 98, 112, 100, 103, 99]])

# # bảng lượng tử ưu tiên sắc độ hình ảnh
# quant = np.array([[17, 18, 24, 47, 99, 99, 99, 99],
#                   [18, 21, 26, 66, 99, 99, 99, 99],
#                   [24, 26, 56, 99, 99, 99, 99, 99],
#                   [47, 66, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99]])

global path_image
time_label = None
img = None


def decode_dct():
    global path_image
    global time_label

    if time_label is not None:
        time_label.destroy()

    start_time = time.process_time()
    img = cv2.imread(path_image)

    row, col = img.shape[:2]
    mesSize = None
    message = ""
    mesBits = list()
    char = list()
    # chia ảnh thành từng kênh màu
    bImg, gImg, rImg = cv2.split(img)

    # thông báo được ẩn trong kênh màu blue nên chuyển đổi thành loại float32
    bImg = np.float32(bImg)

    # Tách thành từng khối 8x8
    # imgBlocks = [bImg[j:j + 8, i:i + 8] - 128 for (j, i) in itertools.product(range(0, row, 8), range(0, col, 8))]
    imgBlocks = [bImg[j:j + 8, i:i + 8] for (j, i) in itertools.product(range(0, row, 8), range(0, col, 8))]

    # Tính giá trị cosin rời rạc cho từng khối bằng hàm dct trong cv2
    imgBlocks = [np.round(cv2.dct(imgBlock)) - 128 for imgBlock in imgBlocks]

    # cho từng khối chạy qua bảng lượng tử hóa theo chiều thuận
    quanDCT = [np.round(img_Block / quant) for img_Block in imgBlocks]
    # print(quanDCT[0:3])

    # thông điệp từ các bit LSB của DC
    i = 0
    for quanBlock in quanDCT:
        DC = quanBlock[0, 0]
        DC = np.uint8(DC)
        DC = np.unpackbits(DC)

        if DC[7] == 1:
            char.append('0')
        elif DC[7] == 0:
            char.append('1')
        i += 1
        if i == 8:
            char = int(''.join(char), 2)
            mesBits.append(chr(char))
            char = list()
            i = 0
            if mesBits[-1] == '*' and mesSize is None:
                try:
                    mesSize = int(''.join(mesBits[:-1]))
                except Exception:
                    pass
        len_str = len(mesBits) - len(str(mesSize)) - 1
        if len_str == mesSize:
            message = ''.join(mesBits)[len(str(mesSize)) + 1:]
            break

    text_time = f"Thời gian giải mã thông điệp: {str(round(time.process_time() - start_time, 3))} giây."
    time_label = Label(app, text=text_time, bg='lavender', font=("calibri", 13), anchor='w')
    time_label.place(x=20, y=360)

    # Hiển thị thông điệp
    txt.delete(1.0, "end")
    txt.insert(1.0, message)
    return


def on_click():
    # khai báo biến toàn cục
    global path_image
    global img

    txt.delete(1.0, "end")

    if img is not None:
        img.destroy()

    if time_label is not None:
        time_label.destroy()
    # sử dụng thư viện tkinter để mở tệp bằng hộp thoại
    # lấy đường dẫn ảnh
    path_image = filedialog.askopenfilename()
    # mở ảnh
    load_image = Image.open(path_image)
    # thiết lập kích cỡ ảnh khi hiển thị
    load_image.thumbnail([300, 300], Image.ANTIALIAS)
    # load image theo mảng array
    np_load_image = np.asarray(load_image)
    np_load_image = Image.fromarray(np.uint8(np_load_image))
    render = ImageTk.PhotoImage(np_load_image)
    img = Label(app, image=render)
    img.image = render
    img.place(x=20, y=50)


# Xây dựng giao diện size 600*400 pixels.
app = Tk()
app.configure(background='lavender')
app.title("Watermaker_DCT-Decode")
app.geometry('600x400')

on_click_button = Button(app, text="Chọn ảnh", bg='white', fg='black', command=on_click)
on_click_button.place(x=250, y=10)

txt = Text(app, wrap=WORD, width=30)
txt.place(x=340, y=55, height=230)

decode_button = Button(app, text="Decode", bg='white', fg='black', command=decode_dct)
decode_button.place(x=435, y=300)

app.mainloop()
