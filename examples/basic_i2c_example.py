from SupernovaController.sequential import SupernovaDevice


def main():
    supernova = SupernovaDevice()

    info = supernova.open()

    result = info.i2c.set_parameters()
    print(result)
    result = info.i2c.write(0x50, [0,0], [33 for i in range(1,129)])
    print(result)
    result = info.i2c.write_non_stop(0x50, [0,0], [55 for i in range(1,129)])
    print(result)
    result = info.i2c.read(0x50, 70)
    print(result)
    result = info.i2c.read_from(0x50, [0,0], 70)
    print(result)

    supernova.close()


if __name__ == "__main__":
    main()
