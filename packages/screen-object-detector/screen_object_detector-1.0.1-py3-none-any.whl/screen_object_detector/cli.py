#!/usr/bin/env python3
"""
CLI интерфейс для screen-object-detector
Позволяет использовать библиотеку через командную строку с флагами
"""

import argparse
import sys
from .screen_detector import ScreenDetector


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description='YOLO детектор объектов на экране',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  screen-detector --model yolov8n.pt --confidence 0.7
  screen-detector --model button.pt --interval 0.2 --duration 60
  screen-detector --clean-output --json results.json
  screen-detector --model game.pt --confidence 0.8 --duration 300 --interval 0.1
        """
    )

    # Флаги программы
    parser.add_argument('--model', '-m',
                       default='your_model.pt',
                       help='Путь к YOLO модели (по умолчанию: your_model.pt)')

    parser.add_argument('--class-id', '-c',
                       type=int, default=0,
                       help='ID класса для поиска (по умолчанию: 0)')

    parser.add_argument('--confidence', '-conf',
                       type=float, default=0.5,
                       help='Коэффициент уверенности модели 0.0-1.0 (по умолчанию: 0.5)')

    parser.add_argument('--interval', '-i',
                       type=float, default=0.5,
                       help='Интервал обновления JSON в секундах (по умолчанию: 0.5)')

    parser.add_argument('--duration', '-d',
                       type=int, default=None,
                       help='Время работы программы в секундах (по умолчанию: бесконечно)')

    parser.add_argument('--json', '-j',
                       default='screen_detections.json',
                       help='Файл для сохранения JSON (по умолчанию: screen_detections.json)')

    parser.add_argument('--clean-output',
                       action='store_true',
                       help='Чистый вывод - показывать только когда click меняется')

    # Парсим аргументы
    args = parser.parse_args()

    # Проверка корректности аргументов
    if not (0.0 <= args.confidence <= 1.0):
        print("Ошибка: коэффициент уверенности должен быть от 0.0 до 1.0")
        sys.exit(1)

    if args.interval <= 0:
        print("Ошибка: интервал обновления должен быть больше 0")
        sys.exit(1)

    if args.duration is not None and args.duration <= 0:
        print("Ошибка: время работы должно быть больше 0")
        sys.exit(1)

    # Вывод настроек
    if not args.clean_output:
        print("Запуск детектора объектов на экране")
        print(f"Модель: {args.model}")
        print(f"ID класса: {args.class_id}")
        print(f"Коэффициент уверенности: {args.confidence}")
        print(f"Интервал обновления: {args.interval} сек")
        print(f"JSON файл: {args.json}")
        if args.duration:
            print(f"Время работы: {args.duration} сек")
        else:
            print("Время работы: бесконечно")
        if args.clean_output:
            print("Режим: чистый вывод (только изменения)")
        print("Нажмите Ctrl+C для остановки\n")

    # Создаем детектор
    try:
        detector = ScreenDetector(
            model_path=args.model,
            target_class_id=args.class_id,
            json_file=args.json,
            confidence_threshold=args.confidence,
            clean_output=args.clean_output
        )

        # Запускаем детекцию
        detector.start_continuous_detection(
            update_interval=args.interval,
            duration=args.duration
        )

    except KeyboardInterrupt:
        print("\nОстановка детектора...")
        if 'detector' in locals():
            detector.stop_detection()
        print("Детектор остановлен")
        if not args.clean_output:
            print(f"Результаты сохранены в: {args.json}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()