import RPi.GPIO as GPIO
import time

# Pin configuration
TRIG = 23
ECHO = 24
LED_PIN = 17
BUZZER_PIN = 22

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# PWM setup (for LED pulse effect)
led_pwm = GPIO.PWM(LED_PIN, 100)  # Frequency: 100Hz
led_pwm.start(0)  # Initial Duty Cycle = 0%
buzzer_pwm = GPIO.PWM(BUZZER_PIN, 659)

def get_distance():
    """
    Measure the distance (in cm) using the ultrasonic distance sensor.
    """
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10μs pulse
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    # Wait for ECHO pin to go HIGH
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
    
    # Wait for ECHO pin to go LOW
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        # Safety mechanism: prevent infinite loop
        if stop_time - start_time > 0.04:  # Consider as out of range if > 40ms
            return 999

    # Calculate distance based on elapsed time (speed of sound: 34300 cm/s)
    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2
    return distance

def pulse_effect():
    """
    Control the LED to create a heartbeat-like pulse effect.
    """
    # Brightening phase
    for duty_cycle in range(0, 101, 5):  # 0% -> 100% (brightening)
        led_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.02)  # Gradual brightening: 20ms delay

    # Dimming phase
    for duty_cycle in range(100, -1, -5):  # 100% -> 0% (dimming)
        led_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.02)  # Gradual dimming: 20ms delay

def activate_feedback():
    """
    Activate LED pulse and buzzer to provide feedback.
    """
    buzzer_pwm.start(50) # Turn on the buzzer
    time.sleep(1000)                 # Run LED pulse effect
    buzzer_pwm.stop() # Turn off the buzzer

def main():
    """
    Main function to detect hand grasping through the distance sensor 
    and provide feedback with LED pulse and buzzer.
    """
    print("Start: Remote hand-holding machine running...")
    try:
        while True:
            distance = get_distance()
            print(f"Current distance: {distance:.2f} cm")

            if distance < 10:  # Grasping detected within 10cm range
                print("Grasp detected! Sending feedback signal.")
                activate_feedback()
            else:
                print("No grasp detected.")

            time.sleep(0.5)  # Wait 0.5 seconds before next measurement
    except KeyboardInterrupt:
        print("\nProgram terminated. Cleaning up GPIO...")
    finally:
        led_pwm.stop()  # Stop PWM
        GPIO.cleanup()

if __name__ == "__main__":
    main()
