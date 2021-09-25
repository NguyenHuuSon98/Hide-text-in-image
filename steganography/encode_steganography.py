from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog
import cv2
import numpy as np
import math
import os
import time

global path_image
image_display_size = 300, 300
img_show = None
img_encode_show = None
label_show = None
time_label = None


def encrypt_data_into_image():
    global path_image
    global time_label
    global label_show

    start_time = time.process_time()

    if label_show is not None:
        label_show.destroy()

    if time_label is not None:
        time_label.destroy()

    if img_encode_show is not None:
        img_encode_show.destroy()

    # lấy nội dung đọc từ dòng 1 ký tự 0
    data = txt.get(1.0, "end-1c")
    # load hình ảnh
    img = cv2.imread(path_image, cv2.IMREAD_UNCHANGED)
    num_char = len(data)
    # tách đoạn văn đến cấp độ ký tự
    # chuyển các kí tự theo bảng mã ASCII sang dạng nhị phân 8-bit
    data = [format(ord(i), '08b') for i in data]
    # số cột pixel
    row, col, chanel = img.shape
    # resize số cột thành bội số của 3
    img = cv2.resize(img, (col + (3 - col % 3), row))

    if chanel == 3:
        pass
    elif chanel == 4:
        bImg, gImg, rImg, aImg = cv2.split(img)
        img = cv2.merge((bImg, gImg, rImg))
    else:
        text = "Lỗi. Ảnh vừa chọn không phải là ảnh RGB!"
        label_show = Label(app, text=text, bg='lavender', font=("Calibri", 14))
        label_show.configure(foreground='red')
        label_show.place(x=155, y=435)
        return

    # len(data) là số kí tự cần mã hóa => số pixel cần thiết bằng 3 lần số kí tự mã hõa
    # vì mỗi pixel sẽ lưu 3 bit trong 3 miền rgb mà 8-bit(1 kí tự) thì cần tối thiểu 3 pixel
    PixReq = len(data) * 3

    # Số hàng pixel cần thiết để lưu văn bản
    RowReq = PixReq / col

    # làm tròn lên
    RowReq = math.ceil(RowReq)

    try:
        count = 0
        charCount = 0
        # Duyệt hình ảnh và thêm từng bit của văn bản vào bit LSB của ảnh
        for i in range(RowReq + 1):
            while count < col and charCount < len(data):
                char = data[charCount]
                charCount += 1
                # Duyệt hình ảnh nếu bit là 1 và giá trị pixel là số chẵn, biến nó thành số lẻ bằng cách trừ đi 1
                # nếu bit là 0 và giá trị pixel là số lẻ, biến nó thành số chẵn bằng cách trừ đi 1.
                for index_k, k in enumerate(char):
                    # Trường hợp đặc biệt nếu bit là 1 và giá trị là 0 thì cộng thêm 1
                    if k == '1' and img[i][count][index_k % 3] == 0:
                        img[i][count][index_k % 3] += 1
                    if (k == '1' and img[i][count][index_k % 3] % 2 == 0) or (k == '0' and img[i][count][index_k % 3] % 2 == 1):
                        img[i][count][index_k % 3] -= 1
                    if index_k % 3 == 2:
                        count += 1
                    if index_k == 7:
                        if charCount * 3 < PixReq and img[i][count][2] % 2 == 1:
                            img[i][count][2] -= 1
                        if charCount * 3 >= PixReq and img[i][count][2] % 2 == 0:
                            if img[i][count][2] == 0:
                                img[i][count][2] = 1
                            else:
                                img[i][count][2] -= 1
                        count += 1
            count = 0
    except Exception as err:
        print(err)
        text = "Thông điệp quá dài không thể nhúng vào ảnh đã chọn!"
        err_label = Label(app, text=text, bg='lavender', font=("Calibri", 14))
        err_label.configure(foreground='red')
        err_label.place(x=120, y=435)
        return

    if chanel == 3:
        pass
    if chanel == 4:
        bImg, gImg, rImg = cv2.split(img)
        img = cv2.merge((bImg, gImg, rImg, aImg))

    # lưu ảnh mới vào file
    if not os.path.exists("image_encode"):
        os.mkdir("image_encode")
    path_save = "image_encode\\image_encode.png"
    cv2.imwrite(path_save, img)
    # print(img.shape)

    img_en_show(path_save)
    # Thời gian chạy
    text_time = f"Kích thước ảnh {row}x{col} | " \
                f"Số ký tự của thông điệp: {num_char} | " \
                f"Thời gian nhúng: {str(round(time.process_time()-start_time, 3))} giây."

    time_label = Label(app, text=text_time, bg='lavender', font=("calibri", 13), anchor='w')
    time_label.place(x=20, y=400)

    # Hiện thông báo thành công.
    success_label = Label(app, text="Nhúng thành công!", bg='lavender', font=("Calibri", 20))
    success_label.place(x=210, y=435)


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


# Xây dựng giao diện
app = Tk()
app.configure(background='lavender')
app.title("Steganography-Encode")
app.geometry('660x500')
# Thêm đường dẫn ảnh
on_click_button = Button(app, text="Chọn ảnh", bg='white', fg='black', command=on_click)
on_click_button.place(x=20, y=10, height=30)
# text box
txt = Text(app, wrap=WORD, width=42)
txt.place(x=150, y=10, height=30)

label_orginal = Label(app, text="Ảnh gốc", bg='lavender', font=("Calibri", 12))
label_orginal.place(x=140, y=55)
label_encode = Label(app, text="Ảnh sau khi nhúng", bg='lavender', font=("Calibri", 12))
label_encode.place(x=430, y=55)

encrypt_button = Button(app, text="Encode", bg='white', fg='black', command=encrypt_data_into_image)
encrypt_button.place(x=500, y=10, height=30)
app.mainloop()
