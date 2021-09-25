import cv2
from tkinter import filedialog, Tk, Button, Label, Text, WORD
from PIL import Image, ImageTk
import numpy as np
import time


global path_image
time_label = None
img = None


def decode():
    global path_image
    global time_label

    if time_label is not None:
        time_label.destroy()

    start_time = time.process_time()
    # Thuật toán lấy thông điệp từ ảnh
    img = cv2.imread(path_image)
    data = []
    stop = False
    for index_i, i in enumerate(img):
        i.tolist()
        for index_j, j in enumerate(i):
            if (index_j % 3) == 2:
                # pixel thứ 1
                data.append(bin(j[0])[-1])
                # pixel thứ 2
                data.append(bin(j[1])[-1])
                # pixel thứ 3
                if bin(j[2])[-1] == '1':
                    stop = True
                    break
            else:
                # pixel thứ 1
                data.append(bin(j[0])[-1])
                # pixel thứ 2
                data.append(bin(j[1])[-1])
                # pixel thứ 3
                data.append(bin(j[2])[-1])
        if(stop):
            break

    message = []

    # nối tất cả các bit để tạo thành các chữ cái (Bảng mã ASCII)
    for i in range(int((len(data)+1)/8)):
        message.append(data[i*8:(i*8+8)])
    # nối tất cả các chữ cái để tạo thành thông điệp
    message = [chr(int(''.join(i), 2)) for i in message]
    message = ''.join(message)

    # Thời gian chạy
    text_time = f"Thời gian giải mã thông điệp: {str(round(time.process_time() - start_time, 3))} giây."
    time_label = Label(app, text=text_time, bg='lavender', font=("calibri", 13), anchor='w')
    time_label.place(x=20, y=360)

    # hiển thị thông điệp
    txt.delete(1.0, "end")
    txt.insert(1.0, message)


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
    # # load image theo mảng array
    np_load_image = np.asarray(load_image)
    np_load_image = Image.fromarray(np.uint8(np_load_image))
    render = ImageTk.PhotoImage(np_load_image)
    img = Label(app, image=render)
    img.image = render
    img.place(x=20, y=50)


# Xây dựng giao diện
app = Tk()
app.configure(background='lavender')
app.title("Steganography-Decode")
app.geometry('600x400')
# Thêm đường dẫn ảnh
on_click_button = Button(app, text="Chọn ảnh", bg='white', fg='black', command=on_click)
on_click_button.place(x=250, y=10)

txt = Text(app, wrap=WORD, width=30)
txt.place(x=340, y=55, height=230)

decode_button = Button(app, text="Decode", bg='white', fg='black', command=decode)
decode_button.place(x=435, y=300)

app.mainloop()

