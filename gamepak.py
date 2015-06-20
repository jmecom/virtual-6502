class GamePak():
    def __init__(self, filename):
        """Loads a .nes file and creates a new GamePak
        http://wiki.nesdev.com/w/index.php/INES#iNES_emulator"""
        with open(filename, "rb") as f:
            # Read file header
            self.header = f.read(16)
            self.parse_header(self.header)

            # If it exists, read trainer
            if self.flag6 & 4:
                self.trainer = f.read(512)

            # Read PRG ROM data
            self.prg_rom = f.read(self.prg_rom_size * 16384)

            # Read CHR ROM data
            self.chr_rom = f.read(self.chr_rom_size * 8192)

    def parse_header(self, header):
        """Checks validity of header format and saves header values"""
        if header[0:4] != b'NES\x1a':
            # Every .nes file needs this constant in the header
            raise Exception("File header is not valid.")

        # TODO handle mapper ids
        self.prg_rom_size = header[4]
        self.chr_rom_size = header[5]
        self.flag6 = header[6]
        self.flag7 = header[7]
        self.prg_ram_size = header[8]
        self.flag9  = header[9]
        self.flag10 = header[10]
