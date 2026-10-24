from pygame import *   
import sounddevice as sd 
import scipy.io.wavfile as wav

# === Налаштування ===
fs = 44100     # Частота дискретизації (кількість вимірів за секунду)
chunk = 1024   # Кількість семплів (відліків) за один кадр
width, height = 800, 400  

init()
screen = display.set_mode((width, height))
display.set_caption("Live Audio (Mic)")
clock = time.Clock()

songs = [
    "456\\MinusDuHast.mp3"
]

current_index = 0
minus_track = songs[current_index]

recording = None
is_recording = False
voice_file = "my_voice.wav"

mixer.init()
mixer.music.set_volume(0.3)

font.init()
font_big = font.SysFont("Arial", 32, bold = True)


btn_record = Rect(425, 250, 200, 80)
btn_record_color = "white"
btn_record_text = "ЗАПИС"

btn_stop = Rect(70, 250, 200, 80)
btn_stop_color = "red"
btn_stop_text = "СТОП"

# Початкові дані — масив нулів (ще немає звуку)
data = [0.0] * chunk

# === Функція, яку викликає sounddevice, коли приходить нова порція звуку ===
def audio_callback(indata, frames, time_info, status):
    global data
    if status:
        print(status)  # Якщо є помилки або попередження, виводимо їх
    # Перетворюємо отриманий звук у список і масштабуємо під висоту екрану
    data = [sample * (height // 2) for sample in indata[:, 0].tolist()]

# === Запуск потоку з мікрофона ===
stream = sd.InputStream(
    callback=audio_callback,  # Функція для отримання аудіо
    channels=1,               # Один канал (моно)
    samplerate=fs,             # Частота дискретизації
    blocksize=chunk,           # Розмір буфера (chunk)
    dtype='float32'            # Тип даних (числа з плаваючою комою)
)
stream.start()

def start_voice_record():
    global recording
    recording = sd.rec(int(fs * 5), samplerate = fs, channels = 1, dtype = "int16")

def stop_voice_record():
    global recording
    sd.stop()
    if recording is not None:
        wav.write(voice_file, fs, recording)

def stop_all_sound():
    mixer.music.stop()
    mixer.stop()

def play_song_and_minus():
    mixer.music.load(minus_track)
    mixer.music.play()
    voice_sound = mixer.Sound(voice_file)
    voice_sound.play()

running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if e.type == MOUSEBUTTONDOWN:
            if btn_record.collidepoint(e.pos):
                if not is_recording:
                    btn_record_color = 'red'
                    btn_record_text = "СТОП"
                    is_recording = True
                    mixer.music.load(minus_track)
                    mixer.music.play()
                    start_voice_record()
                else:
                    btn_record_color = "white"
                    btn_record_text = "ЗАПИС"
                    is_recording = False
                    stop_voice_record()
                    play_song_and_minus()

            if btn_stop.collidepoint(e.pos):
                stop_all_sound()
                is_recording = False


    screen.fill((0, 0, 0))

    # Готуємо список точок для малювання хвилі
    points = []
    for i, sample in enumerate(data):
        x = int(i * width / chunk)          # Позиція X для точки
        y = int(height / 2 + sample)        # Позиція Y для точки
        points.append((x, y))               # Додаємо точку в список

    # Малюємо лінію по точках, якщо їх більше однієї
    if len(points) > 1:
        draw.lines(screen, (0, 255, 0), False, points, 2)


    draw.rect(screen, btn_record_color, btn_record)
    rec_text = font_big.render(btn_record_text, True, "black")
    screen.blit(rec_text, (btn_record.x + 20, btn_record.y + 20))

    draw.rect(screen, btn_stop_color, btn_stop)
    stop_text = font_big.render(btn_stop_text, True, "black")
    screen.blit(stop_text, (btn_stop.x + 20, btn_stop.y + 20))


    display.update()
    clock.tick(60)

stream.stop()
quit()
