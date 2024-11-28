import RPi.GPIO as GPIO
import time

# 핀 번호 설정
TRIG = 23
ECHO = 24
LED_PIN = 17
BUZZER_PIN = 22

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# PWM 설정 (LED 펄스 효과를 위해)
led_pwm = GPIO.PWM(LED_PIN, 100)  # 주파수 100Hz
led_pwm.start(0)  # 초기 Duty Cycle = 0%

def get_distance():
    """
    초음파 거리 센서를 이용해 현재 거리(cm)를 측정하는 함수.
    """
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10μs 펄스
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    # 신호 발사 후 ECHO 핀에서 신호가 들어오기까지 대기
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
    
    # ECHO 핀이 신호를 잃을 때까지 대기
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        # 안전장치: 무한 루프 방지
        if stop_time - start_time > 0.04:  # 40ms 이상이면 거리 초과로 간주
            return 999

    # 시간 차이를 계산하여 거리 계산 (음속: 34300 cm/s)
    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2
    return distance

def pulse_effect():
    """
    LED를 심장 박동처럼 밝아졌다가 어두워지는 펄스 효과로 제어.
    """
    # 점점 밝아지는 구간
    for duty_cycle in range(0, 101, 5):  # 0% -> 100% (밝아짐)
        led_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.02)  # 천천히 밝아지도록 20ms 대기

    # 점점 어두워지는 구간
    for duty_cycle in range(100, -1, -5):  # 100% -> 0% (어두워짐)
        led_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.02)  # 천천히 어두워지도록 20ms 대기

def activate_feedback():
    """
    LED 펄스와 부저를 활성화하여 피드백을 전달하는 함수.
    """
    GPIO.output(BUZZER_PIN, True)  # 부저 켜기
    pulse_effect()                 # LED 펄스 효과 실행
    GPIO.output(BUZZER_PIN, False) # 부저 끄기

def main():
    """
    거리 센서를 통해 손잡기 상태를 감지하고 LED 펄스와 부저로 피드백을 전달하는 메인 함수.
    """
    print("시작: 원격 손잡기 기계 작동 중...")
    try:
        while True:
            distance = get_distance()
            print(f"현재 거리: {distance:.2f} cm")

            if distance < 10:  # 손잡기 감지 거리 (10cm 이하)
                print("손잡기 감지됨! 신호를 보냅니다.")
                activate_feedback()
            else:
                print("손잡기 감지되지 않음.")

            time.sleep(0.5)  # 0.5초 대기 후 다시 측정
    except KeyboardInterrupt:
        print("\n프로그램 종료. GPIO 정리 중...")
    finally:
        led_pwm.stop()  # PWM 중지
        GPIO.cleanup()

if __name__ == "__main__":
    main()
