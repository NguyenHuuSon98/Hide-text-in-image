import os
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
# bảng lượng tử ưu tiên sắc độ hình ảnh
# quant = np.array([[17, 18, 24, 47, 99, 99, 99, 99],
#                   [18, 21, 26, 66, 99, 99, 99, 99],
#                   [24, 26, 56, 99, 99, 99, 99, 99],
#                   [47, 66, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99],
#                   [99, 99, 99, 99, 99, 99, 99, 99]])

global path_image
image_display_size = 300, 300
img_show = None
img_encode_show = None
label_show = None
time_label = None


def encode_dct():
    global label_show
    global time_label

    start_time = time.process_time()

    if label_show is not None:
        label_show.destroy()

    if time_label is not None:
        time_label.destroy()

    if img_encode_show is not None:
        img_encode_show.destroy()

    secret = txt.get(1.0, "end-1c")
    img = cv2.imread(path_image, cv2.IMREAD_UNCHANGED)
    message = str(len(secret)) + "*" + secret

    # format(ord(i), '08b') chuyển các kí tự sang dạng nhị phân 8-bit
    bitMess = [format(ord(i), '08b') for i in message]
    row, col, chanel = img.shape

    # làm tròn(lên) các pixel thành bội số của 8
    if row % 8 != 0 or col % 8 != 0:
        # mặc định resize theo phương pháp INTER_LINEAR (nội suy xong tuyến) sử dụng 4 điểm ảnh gần nhất để tính giá trị của điểm ảnh mới.
        img = cv2.resize(img, (col + (8 - col % 8), row + (8 - row % 8)))

    # lấy lại số hàng và cột của ảnh mới sau khi resize
    row, col = img.shape[:2]

    # liểm tra xem kích thước ảnh có đủ để lưu thông điệp hay không
    numBlockImg8px = (col / 8) * (row / 8)
    if numBlockImg8px < len(message)*8:
        text = "Thông điệp quá dài không thể nhúng vào ảnh đã chọn!"
        label_show = Label(app, text=text, bg='lavender', font=("Calibri", 14))
        label_show.configure(foreground='red')
        label_show.place(x=120, y=435)
        return

    # chia ảnh thành từng kênh màu
    if chanel == 3:
        bImg, gImg, rImg = cv2.split(img)
    elif chanel == 4:
        bImg, gImg, rImg, aImg = cv2.split(img)
    else:
        text = "Lỗi. Ảnh vừa chọn không phải là ảnh RGB!"
        label_show = Label(app, text=text, bg='lavender', font=("Calibri", 14))
        label_show.configure(foreground='red')
        label_show.place(x=155, y=435)
        return

    # print(bImg)
    # thông báo được ẩn trong kênh màu blue nên chuyển đổi thành loại float32
    bImg = np.float32(bImg)

    # cắt ảnh thành từng khối 8x8 pixel
    # vì hàm cosin nằm trong khoảng (-1,1) mà giá trị màu nằm trong khoảng (0, 255)
    # vì vậy ta cần lấy điểm chính giữ tương đương với điểm 0 trong hàm cosin bằng cách trừ đi 128
    imgBlocks = [np.round(bImg[i:i + 8, j:j + 8] - 128) for (i, j) in
                 itertools.product(range(0, row, 8), range(0, col, 8))]

    # Tính giá trị cosin rời rạc cho từng khối bằng hàm dct trong cv2
    dctBlocks = [np.round(cv2.dct(img_Block)) for img_Block in imgBlocks]

    # cho từng khối chạy qua bảng lượng tử hóa
    quantizedDCT = [np.round(dct_Block / quant) for dct_Block in dctBlocks]

    # đặt LSB ở giá trị bit DC tương ứng của message
    charIndex = 0
    endIndexOfChar = 0
    for quantizedBlock in quantizedDCT:
        DC = quantizedBlock[0][0]
        DC = np.uint8(DC)  # chuyển về số nguyên trong khoảng (0,255) <=> 255 % DC (1)
        DC = np.unpackbits(DC)  # giải nén các phần tử của một mảng uint8 thành một mảng đầu ra có giá trị nhị phân
        DC[7] = bitMess[charIndex][endIndexOfChar]  # thay 1 bit của message cho 1 bit cuối của DC
        DC = np.packbits(DC)
        DC = np.float32(DC)
        DC = DC - 255  # trả lại kiểu giá trị tương đương như trước khi thay đổi ở (1)
        quantizedBlock[0][0] = DC
        endIndexOfChar = endIndexOfChar + 1
        if endIndexOfChar == 8:
            endIndexOfChar = 0
            charIndex = charIndex + 1
            if charIndex == len(message):  # Check
                break

    # print(quantizedDCT[0:3])
    # Cho các khối chạy nghịch đảo qua bảng lượng tử hóa
    # sImgBlocks = [quantizedBlock * quant + 128 for quantizedBlock in quantizedDCT]

    newImgBlocks = [(quantizedBlock * quant) for quantizedBlock in quantizedDCT]
    sImgBlocks = [np.round(cv2.idct(newImgBlock)) + 128 for newImgBlock in newImgBlocks]

    newbImg = []
    for rowBlocks in numCol(sImgBlocks, col / 8):
        for numRowBlock in range(0, 8):
            for block in rowBlocks:
                newbImg.extend(block[numRowBlock])

    newbImg = np.array(newbImg).reshape(row, col)
    newbImg = np.uint8(newbImg)

    # print(newbImg)
    if chanel == 3:
        newImg = cv2.merge((newbImg, gImg, rImg))
    if chanel == 4:
        newImg = cv2.merge((newbImg, gImg, rImg, aImg))

    # thời gian của quá trình nhúng thông điệp
    print(time.process_time()-start_time, ' giây')

    if not os.path.exists("image_encode"):
        os.mkdir("image_encode")
    path_save = "image_encode\\dct_encode_image.png"
    cv2.imwrite(path_save, newImg)

    img_en_show(path_save)

    # Thời gian chạy
    text_time = f"Kích thước ảnh {row}x{col} | " \
                f"Số ký tự của thông điệp: {len(secret)} | " \
                f"Thời gian nhúng: {str(round(time.process_time()-start_time, 3))} giây."

    time_label = Label(app, text=text_time, bg='lavender', font=("calibri", 13), anchor='w')
    time_label.place(x=20, y=400)

    # Hiện thông báo thành công.
    label_show = Label(app, text="Nhúng thành công!", bg='lavender', font=("Calibri", 20))
    label_show.place(x=210, y=435)
    return


# trả về từng hàng của ảnh
def numCol(imgBlocks, n):
    m = int(n)
    for i in range(0, len(imgBlocks), m):
        yield imgBlocks[i:i + m]


# Sử lý khi click để lấy link ảnh với thư viện tkinter
def on_click():
    # khai báo biến toàn cục
    global path_image
    global img_show

    if img_show is not None:
        img_show.destroy()

    if img_encode_show is not None:
        img_encode_show.destroy()

    if label_show is not None:
        label_show.destroy()

    if time_label is not None:
        time_label.destroy()
    # sử dụng thư viện tkinter để mở tệp bằng hộp thoại
    # lấy đường dẫn ảnh
    path_image = filedialog.askopenfilename()
    # mở ảnh
    load_image = Image.open(path_image)
    # thiết lập kích cỡ ảnh khi hiển thị
    load_image.thumbnail(image_display_size, Image.ANTIALIAS)
    # load image theo mảng array
    np_load_image = np.asarray(load_image)
    np_load_image = Image.fromarray(np.uint8(np_load_image))
    render = ImageTk.PhotoImage(np_load_image)
    img_show = Label(app, image=render)
    img_show.image = render
    img_show.place(x=20, y=80)
    return


def img_en_show(path_img_encode):
    global img_encode_show
    # if img_encode_show is not None:
    #     img_encode_show.destroy()

    img_encode = Image.open(path_img_encode)
    img_encode.thumbnail(image_display_size, Image.ANTIALIAS)
    img_encode = np.asarray(img_encode)
    img_encode = Image.fromarray(np.uint8(img_encode))
    render = ImageTk.PhotoImage(img_encode)
    img_encode_show = Label(app, image=render)
    img_encode_show.image = render
    img_encode_show.place(x=340, y=80)
    return


# Xây dựng giao diện.
app = Tk()
app.configure(background='lavender')
app.title("Watermaker_DCT-Encode")
app.geometry('660x500')
# Thêm đường dẫn ảnh
on_click_button = Button(app, text="Chọn ảnh", bg='white', fg='black', command=on_click)
on_click_button.place(x=20, y=10, height=30)
# text box
txt = Text(app, wrap=WORD, width=42)
txt.place(x=150, y=10, height=30)

label_orginal = Label(app, text="ảnh gốc", bg='lavender', font=("Calibri", 12))
label_orginal.place(x=140, y=55)
label_encode = Label(app, text="ảnh sau khi nhúng", bg='lavender', font=("Calibri", 12))
label_encode.place(x=430, y=55)

encrypt_button = Button(app, text="Encode", bg='white', fg='black', command=encode_dct)
encrypt_button.place(x=500, y=10, height=30)
app.mainloop()
