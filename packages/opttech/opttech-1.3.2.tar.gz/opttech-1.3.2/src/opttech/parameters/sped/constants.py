from pathlib import Path

SPED_RULES_FOLDER = str(Path(__file__).parent / 'sped_rules')
TABLES_FOLDER = str(Path(__file__).parent / 'tables')


MANAD_SINTETICO_SUMMARY_PARAMETERS = {
    'K300M_DT_COMP' : 'GROUPBY', 
    'K300M_COD_RUBR' : 'GROUPBY', 
    'K150M_DESC_RUBRICA' : 'GROUPBY', 
    'K300M_VLR_RUBR' : 'SUM', 
    'K300M_CNPJ/CEI' : 'GROUPBY', 
    'K300M_IND_RUBR' : 'GROUPBY',
    'K300M_IND_FL' : 'GROUPBY'
}

MANAD_DESCR_RUBR = {
    'D' : 'Desconto',
    'P' : 'Provento ou Vantagem',
    'O' : 'Outros'
}

MANAD_DESCR_FL = {
    '1' : 'Folha normal',
    '2' : 'Folha de 13º salário',
    '3' : 'Folha de férias',
    '4' : 'Folha complementar à normal',
    '5' : 'Folha complementar ao 13º',
    '6' : 'Outras folhas'
}

MANAD_SORT_PARAMETERS = {
    'K300M_DT_COMP' : 'MMYYYY',
    'K300M_CNPJ/CEI' : None
}


SPED_BY_VERSION = {
    'MANAD' : {
        '001' : {
            'prefixo' : 'M',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : False
        },
        '002' : {
            'prefixo' : 'M',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : False
        },
        '003' : {
            'prefixo' : 'M',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : False
        }
    },
    'ECD' : {
        '2009' : {
            'version' : '0001',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2010' : {
            'version' : '0001',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2011' : {
            'version' : '0001',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2012' : {
            'version' : '0001',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2013' : {
            'version' : '0002',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2014' : {
            'version' : '0003',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2015' : {
            'version' : '0004',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2016' : {
            'version' : '0005',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2017' : {
            'version' : '0006',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2018' : {
            'version' : '0007',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2019' : {
            'version' : '0008',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2020' : {
            'version' : '0009',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2021' : {
            'version' : '0009',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2022' : {
            'version' : '0009',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2023' : {
            'version' : '0009',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
        '2024' : {
            'version' : '0009',
            'prefixo' : 'ECD',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True
        },
    },
    'ECF' : {
        '0001' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0002' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0003' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0004' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0005' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0006' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0007' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0008' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0009' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '0010' : {
            'prefixo' : 'ECF',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        }
    },
    'EFD_CONTR' : {
        '002' : {
            'prefixo' : 'C',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '003' : {
            'prefixo' : 'C',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '004' : {
            'prefixo' : 'C',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '005' : {
            'prefixo' : 'C',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '006' : {
            'prefixo' : 'C',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        }
    },
    'EFD_FISCAL' : {
        '001' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '002' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '003' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '004' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '005' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '006' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '007' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '008' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '009' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '010' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '011' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '012' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '013' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '014' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '015' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '016' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '017' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '018' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        },
        '019' : {
            'prefixo' : 'F',
            'encoding' : 'ISO-8859-1',
            'delimiter' : '|',
            'delimiter_start' : True,
            'generate_crossovers' : 'yes'
        }        
    }
}



REPORT_REG_COMPL = {
    "EFD_CONTR" : {
        "0500" : {
            "fields" : [ "COD_CTA" ],
            "0500" : [ "0500C_COD_CTA" ]
        },
        "0200" : {
            "fields" : [ "COD_ITEM" ],
            "0200" : [ "0200C_COD_ITEM" ]
        },
        "0150" : {
            "fields" : [ "COD_PART" ],
            "0150" : [ "0150C_COD_PART" ]
        },
        "0140" : {
            "fields" : [ "CNPJ" ],
            "0140" : [ "0140C_CNPJ" ]
        }
    },
    "EFD_FISCAL" : {
        "0500" : {
            "fields" : [ "COD_CTA" ],
            "0500" : [ "0500F_COD_CTA" ]
        },
        "0200" : {
            "fields" : [ "COD_ITEM" ],
            "0200" : [ "0200F_COD_ITEM" ]
        },
        "0150" : {
            "fields" : [ "COD_PART" ],
            "0150" : [ "0150F_COD_PART" ]
        }
    },
    "ECF" : {},
    "ECD" : {
        "I050" : {
            "fields" : [ "COD_CTA" ],
            "I050" : [ "I050ECD_COD_CTA" ]
        },
        "I051" : {
            "fields" : [ "COD_CTA" ],
            "I051" : [ "I050ECD_COD_CTA" ]
        }
    },
    "MANAD" : {
        "K150" : {
            "fields" : [ "COD_RUBR" ],
            "K150" : [ "K150M_COD_RUBRICA" ]
        },
        "K100" : {
            "fields" : [ "COD_LTC" ],
            "K100" : [ "K100M_COD_LTC" ],
            "filter" : set(["K100M_REG", "K100M_DT_INC_ALT", "K100M_COD_LTC", "K100M_CNPJ/CEI", "K100M_CNPJ/CEI_TOM"])
        },
        "K050" : {
            "fields" : [ "CNPJ/CEI", "COD_REG_TRAB" ],
            "filter" : set(["K050M_REG", "K050M_CNPJ/CEI", "K050M_DT_INC_ALT", "K050M_COD_REG_TRAB"]),
            "K050" : [ "K050M_CNPJ/CEI", "K050M_COD_REG_TRAB" ]
        }
    }
}


REPORT_REG = {
    "EFD_CONTR" : {
        "A110" : 0, #INSERI NOVO 04012024
        "A111" : 0, #INSERI NOVO 04012024
        "A120" : 0, #INSERI NOVO 04012024
        "A170" : 0,
        "C100" : 0, #INSERI NOVO 23072024
        "C110" : 0, #INSERI NOVO 04012024
        "C111" : 0, #INSERI NOVO 04012024
        "C120" : 0, #INSERI NOVO 04012024
        "C170" : 0,
        "C175" : 0,
        "C180" : 1,
        "C190" : 1,
        "C380" : 1,
        "C395" : 1,
        "C405" : 1,
        "C489" : 0,
        "C490" : 1,
        "C500" : 1,
        "C600" : 1,
        "C800" : 1,
        "C860" : 1,
        "D100" : 1,
        "D200" : 1,
        "D300" : 1,
        "D350" : 1,
        "D500" : 1,
        "D600" : 1, #INSERI NOVO 04012024
        "F100" : 1,
        "F120" : 1,
        "F130" : 1,
        "F150" : 0,
        "F200" : 1,
        "F500" : 1,
        "F510" : 1,
        "F525" : 1,
        "F550" : 1,
        "F560" : 1,
        "F600" : 0,
        "F700" : 0,
        "F800" : 0,
        "I200" : 2,
        "I100" : 1,
        "M100" : 0, #INSERI NOVO 14022024
        "M105" : 0, #INSERI NOVO 14022024
        "M110" : 0, #INSERI NOVO 14022024
        "M115" : 0, #INSERI NOVO 14022024
        "M200" : 0, #INSERI NOVO 14022024
        "M205" : 0, #INSERI NOVO 14022024
        "M210" : 0, #INSERI NOVO 14022024
        "M211" : 0, #INSERI NOVO 04012024
        "M215" : 0, #INSERI NOVO 04012024
        "M220" : 0, #INSERI NOVO 04012024
        "M225" : 0, #INSERI NOVO 04012024
        "M230" : 0, #INSERI NOVO 04012024
        "M300" : 0,
        "M350" : 0,
        "M400" : 1,
        "M500" : 0,
        "M505" : 0,
        "M510" : 0,
        "M515" : 0,
        "M600" : 0, #INSERI NOVO 14022024
        "M605" : 0, #INSERI NOVO 14022024
        "M610" : 0, #INSERI NOVO 14022024
        "M611" : 0, #INSERI NOVO 14022024
        "M615" : 0, #INSERI NOVO 14022024
        "M620" : 0, #INSERI NOVO 14022024
        "M625" : 0, #INSERI NOVO 14022024
        "M630" : 0, #INSERI NOVO 14022024
        "M700" : 0,
        "M800" : 1,
        "P100" : 1,
        "P200" : 1,
        "1010" : 1,
        "1020" : 0, #INSERI NOVO 04012024
        "1050" : 0, #INSERI NOVO 04012024
        "1100" : 2,
        "1200" : 1,
        "1300" : 1,
        "1500" : 2,
        "1600" : 1,
        "1700" : 1,
        "1800" : 1,
        "1900" : 0
    },
    "EFD_FISCAL" : {
        "B020" : 1,
        "B030" : 1,
        "B350" : 0,
        "B420" : 0,
        "B440" : 0,
        "B460" : 0,
        "B470" : 0,
        "B500" : 1,
        "C100" : 0, #INSERI NOVO 23072024
        "C101" : 1, #INSERI NOVO 04012024
        "C105" : 1, #INSERI NOVO 04012024
        "C110" : 1, #INSERI NOVO 04012024
        "C120" : 0, #INSERI NOVO 04012024
        "C130" : 0, #INSERI NOVO 04012024
        "C140" : 1, #INSERI NOVO 04012024
        "C160" : 0, #INSERI NOVO 04012024
        "C165" : 0, #INSERI NOVO 04012024
        "C170" : 0,
        "C180" : 0, #INSERI NOVO 15022024
        "C181" : 0, #INSERI NOVO 15022024
        "C185" : 0,
        "C186" : 0,
        "C190" : 1,
        "C195" : 1,
        "C300" : 3,
        "C321" : 0, #INSERI NOVO 19022024
        "C350" : 2, #INSERI NOVO 04012024
        "C380" : 0,
        "C390" : 0,
        "C405" : 3,
        "C490" : 0, #INSERI NOVO 19022024
        "C495" : 0,
        "C500" : 0,
        "C510" : 0, #INSERI NOVO 18022024
        "C590" : 0, #INSERI NOVO 18022024
        "C591" : 0, #INSERI NOVO 18022024
        "C595" : 0, #INSERI NOVO 18022024
        "C597" : 0, #INSERI NOVO 18022024
        "C600" : 1,
        "C690" : 0, #INSERI NOVO 19022024
        "C700" : 2,
        "C790" : 0, #INSERI NOVO 19022024
        "C800" : 2,
        "C850" : 0, #INSERI NOVO 19022024
        "C860" : 2,
        "C890" : 0,
        "D100" : 0,
        "D101" : 0, #INSERI NOVO 16022024
        "D110" : 0, #INSERI NOVO 16022024
        "D120" : 0, #INSERI NOVO 16022024
        "D130" : 0, #INSERI NOVO 16022024
        "D140" : 0, #INSERI NOVO 16022024
        "D150" : 0, #INSERI NOVO 16022024
        "D160" : 0, #INSERI NOVO 16022024
        "D161" : 0, #INSERI NOVO 16022024
        "D162" : 0, #INSERI NOVO 16022024
        "D170" : 0, #INSERI NOVO 16022024
        "D180" : 0, #INSERI NOVO 16022024
        "D190" : 0, #INSERI NOVO 16022024
        "D195" : 0, #INSERI NOVO 16022024
        "D197" : 0, #INSERI NOVO 16022024
        "D300" : 1,
        "D350" : 3,
        "D400" : 2,
        "D500" : 1,
        "D600" : 1,
        "D695" : 2,
        "D700" : 2,
        "D750" : 2,
        "E110" : 0,
        "E111" : 0,
        "E112" : 0,
        "E113" : 0,
        "E115" : 0,
        "E116" : 0,
        "E200" : 0,
        "E210" : 0,
        "E220" : 0,
        "E230" : 0,
        "E240" : 0,
        "E250" : 0,
        "E300" : 3,
        "E500" : 0,
        "E510" : 0,
        "E520" : 0,
        "E530" : 0,
        "E531" : 0,
        "G125" : 0, #INSERI NOVO 04012024
        "G126" : 1,
        "G130" : 1,
        "H005" : 2,
        "K100" : 2,
        "1010" : 0, #INSERI NOVO 04012024
        "1100" : 2, #INSERI NOVO 04012024
        "1200" : 1, #INSERI NOVO 04012024
        "1250" : 1, #INSERI NOVO 04012024
        "1300" : 2, #INSERI NOVO 04012024
        "1350" : 1, #INSERI NOVO 04012024
        "1390" : 1, #INSERI NOVO 04012024
        "1400" : 0, #INSERI NOVO 04012024
        "1500" : 1, #INSERI NOVO 04012024
        "1600" : 0, #INSERI NOVO 04012024
        "1601" : 0, #INSERI NOVO 04012024
        "1700" : 1, #INSERI NOVO 04012024
        "1800" : 0, #INSERI NOVO 04012024
        # "1900" : 4, #INSERI NOVO 04012024 ( - N3 30052024 - )
        "1960" : 0, #INSERI NOVO 04012024
        "1970" : 1, #INSERI NOVO 04012024
        "1980" : 0, #INSERI NOVO 04012024
    },
    "ECF" : {
        "E010" : 1,
        "E020" : 0,
        "E030" : 1,
        "C050" : 0,
        "C051" : 0,
        "C100" : 0,
        "C150" : 2,
        "C350" : 1,    
        "J050" : 1,
        "J100" : 0,
        "K155" : 1,
        "K355" : 1,
        "K915" : 0,
        "K935" : 0,
        "L100" : 0,
        "L200" : 0,
        "L210" : 0,
        "L300" : 0,
        "M010" : 0, #INSERI NOVO 27062024
        "M300" : 2,
        "M350" : 2,
        "M410" : 1,
        "M500" : 0,
        "M510" : 0,
        "N500" : 0,
        "N600" : 0,
        "N605" : 0, #INSERI NOVO 04012024
        "N610" : 0,
        "N615" : 0,
        "N620" : 0,
        "N630" : 0,
        "N650" : 0,
        "N660" : 0,
        "N670" : 0,
        "P100" : 0,
        "P130" : 0,
        "P150" : 0,
        "P200" : 0,
        "P230" : 0,
        "P300" : 0,
        "P400" : 0,
        "P500" : 0,
        "Q100" : 0,
        "T030" : 1,
        "U100" : 0,
        "U150" : 0,
        "U180" : 0,
        "U182" : 0,
        "V020" : 0,
        "V030" : 0,
        "V100" : 0,
        "W100" : 2,
        "W300" : 0,
        "X280" : 0,
        "X291" : 0,
        "X292" : 0,
        "X300" : 0, #INSERI NOVO 04012024
        "X305" : 0,
        "X310" : 0,
        "X320" : 0, #INSERI NOVO 04012024
        "X325" : 0,
        "X330" : 0,
        "X340" : 0, #INSERI NOVO 04012024
        "X350" : 0,
        "X351" : 0,
        "X352" : 0,
        "X353" : 0,
        "X354" : 0,
        "X355" : 0,
        "X356" : 0,
        "X357" : 0,
        "X360" : 0, #INSERI NOVO 04012024
        "X365" : 0, #INSERI NOVO 04012024
        "X366" : 0, #INSERI NOVO 04012024
        "X370" : 0, #INSERI NOVO 04012024
        "X371" : 0, #INSERI NOVO 04012024
        "X375" : 0, #INSERI NOVO 04012024
        "X390" : 0,
        "X400" : 0,
        "X410" : 0,
        "X420" : 0,
        "X430" : 0,
        "X450" : 0,
        "X460" : 0,
        "X470" : 0,
        "X480" : 0,
        "X485" : 0, #INSERI NOVO 04012024
        "X490" : 0,
        "X500" : 0,
        "X510" : 0,
        "Y520" : 0,
        "Y540" : 0,
        "Y550" : 0,
        "Y560" : 0,
        "Y570" : 0,
        "Y580" : 0,
        "Y590" : 0,
        "Y600" : 0,
        "Y612" : 0,
        "Y620" : 0,
        "Y630" : 0,
        "Y640" : 0,
        "Y650" : 0,
        "Y660" : 0,
        "Y671" : 0,
        "Y672" : 0,
        "Y680" : 1,
        "Y682" : 0,
        "Y690" : 0,
        "Y720" : 0,
        "Y750" : 0,
        "Y800" : 0,
    },
    "ECD" : {
        "C050" : 1,
        "C150" : 1,
        "C600" : 1,
        "I012" : 1,
        "I020" : 0,
        "I030" : 0,
        "I050" : 1,
        "I075" : 0,
        "I100" : 0,
        "I150" : 2,
        "I200" : 1,
        "I300" : 1,
        "I350" : 1,
        "I500" : 0,
        "I510" : 0,
        "I550" : 1,
        "J100" : 0,
        "J150" : 0,
        "J210" : 1,
        "J800" : 0,
        "J801" : 0,
        "J900" : 1,
        "K100" : 2,
        "K200" : 1,
        "K300" : 2,
    },
    "MANAD" : {
        "0000" : None,
        "0001" : None,
        "0050" : None,
        "0100" : None,
        "0990" : None,
        "I001" : None,
        "I005" : None,
        "I050" : None,
        "I100" : None,
        "I150" : None,
        "I200" : None,
        "I990" : None,
        "K001" : None,
        "K050" : None,
        "K100" : None,
        "K150" : None,
        "K200" : None,
        "K250" : None,
        "K300" : None,
        "K990" : None,
        "L001" : None,
        "L150" : None,
        "L200" : None,
        "L250" : None,
        "L300" : None,
        "L350" : None,
        "L400" : None,
        "L450" : None,
        "L500" : None,
        "L550" : None,
        "L600" : None,
        "L650" : None,
        "L700" : None,
        "L750" : None,
        "L800" : None,
        "L990" : None,
        "9001" : None,
        "9900" : None,
        "9990" : None,
        "9999" : None
    }
}



SUMMARY_BY_REPORT = {
    "EFD_CONTR" : {
        '1010' : { '1011C_DESC_DOC_OPER': [0, 0]},
        '1100' : { '1102C_VL_CRED_PIS_': [0, 0], 'EXP': [0, 0]},
        '1200' : { '1220C_VL_CRED': [0, 0]},
        '1300' : { '1300C_SLD_RET': [0, 0]},
        '1500' : { '1502C_VL_CRED_COFINS_': [0, 0], 'EXP': [0, 0]},
        '1600' : { '1620C_VL_CRED': [0, 0]},
        '1700' : { '1700C_SLD_RET': [0, 0]},
        '1800' : { '1809C_IND_PROC': [0, 0]},
        '1900' : { '1900C_COD_CTA': [0, 0]},
        'A110' : { 'A110C_REG': [0, 0]},
        'A111' : { 'A111C_REG': [0, 0]},
        'A120' : { 'A120C_REG': [0, 0]},
        "A170" : { 'A170C_VL_ITEM': [0,0], 'A170C_VL_BC_PIS' : [0,0], 'A170C_VL_PIS' : [0,0], 'A170C_VL_BC_COFINS' : [0,0], 'A170C_VL_COFINS' : [0,0] },
        'C110' : { 'C110C_REG': [0, 0]},
        'C111' : { 'C111C_REG': [0, 0]},
        'C120' : { 'C120C_REG': [0, 0]},
        "C170" : { 'C170C_VL_ITEM': [0,0], 'C170C_VL_BC_PIS' : [0,0], 'C170C_VL_PIS' : [0,0], 'C170C_VL_BC_COFINS' : [0,0], 'C170C_VL_COFINS' : [0,0] },
        "C175" : { 'C175C_VL_OPR' : [0,0], 'C175C_VL_BC_PIS' : [0,0], 'C175C_VL_PIS' : [0,0], 'C175C_VL_BC_COFINS' : [0,0], 'C175C_VL_COFINS' : [0,0] },
        "C180" : { 'C181C_VL_ITEM': [0,0], 'C181C_VL_BC_PIS' : [0,0], 'C181C_VL_PIS' : [0,0], 'C185C_VL_ITEM' : [0,0], 'C185C_VL_BC_COFINS' : [0,0], 'C185C_VL_COFINS' : [0,0] },
        "C190" : { 'C191C_VL_ITEM': [0,0], 'C191C_VL_BC_PIS' : [0,0], 'C191C_VL_PIS' : [0,0], 'C195C_VL_ITEM' : [0,0], 'C195C_VL_BC_COFINS' : [0,0], 'C195C_VL_COFINS' : [0,0] },
        "C380" : { 'C381C_VL_ITEM': [0,0], 'C381C_VL_BC_PIS' : [0,0], 'C381C_VL_PIS' : [0,0], 'C385C_VL_ITEM' : [0,0], 'C385C_VL_BC_COFINS' : [0,0], 'C385C_VL_COFINS' : [0,0] },
        'C395' : { 'C396C_VL_COFINS': [0, 0]},
        "C405" : { 'C481C_VL_ITEM': [0,0], 'C481C_VL_BC_PIS' : [0,0], 'C481C_VL_PIS' : [0,0], 'C485C_VL_ITEM' : [0,0], 'C485C_VL_BC_COFINS' : [0,0], 'C485C_VL_COFINS' : [0,0] },
        'C489' : { 'C489C_IND_PROC': [0, 0]},
        "C490" : { 'C491C_VL_ITEM': [0,0], 'C491C_VL_BC_PIS' : [0,0], 'C491C_VL_PIS' : [0,0], 'C495C_VL_ITEM' : [0,0], 'C495C_VL_BC_COFINS' : [0,0], 'C495C_VL_COFINS' : [0,0] },
        "C500" : { 'C501C_VL_ITEM': [0,0], 'C501C_VL_BC_PIS' : [0,0], 'C501C_VL_PIS' : [0,0], 'C505C_VL_ITEM' : [0,0], 'C505C_VL_BC_COFINS' : [0,0], 'C505C_VL_COFINS' : [0,0] },
        "C600" : { 'C601C_VL_ITEM': [0,0], 'C601C_VL_BC_PIS' : [0,0], 'C601C_VL_PIS' : [0,0], 'C605C_VL_ITEM' : [0,0], 'C605C_VL_BC_COFINS' : [0,0], 'C605C_VL_COFINS' : [0,0] },
        "C800" : { 'C810C_VL_ITEM': [0,0], 'C810C_VL_BC_PIS' : [0,0], 'C810C_VL_PIS' : [0,0], 'C820C_VL_ITEM' : [0,0], 'C820C_VL_BC_COFINS' : [0,0], 'C820C_VL_COFINS' : [0,0] },
        "C860" : { 'C870C_VL_ITEM': [0,0], 'C870C_VL_BC_PIS' : [0,0], 'C870C_VL_PIS' : [0,0], 'C880C_VL_ITEM' : [0,0], 'C880C_VL_BC_COFINS' : [0,0], 'C880C_VL_COFINS' : [0,0] },
        "D100" : { 'D101C_VL_ITEM': [0,0], 'D101C_VL_BC_PIS' : [0,0], 'D101C_VL_PIS' : [0,0], 'D105C_VL_ITEM' : [0,0], 'D105C_VL_BC_COFINS' : [0,0], 'D105C_VL_COFINS' : [0,0] },
        'D200' : { 'D209C_IND_PROC': [0, 0]},
        'D300' : { 'D309C_IND_PROC': [0, 0]},
        'D350' : { 'D359C_IND_PROC': [0, 0]},
        "D500" : { 'D501C_VL_ITEM': [0,0], 'D501C_VL_BC_PIS' : [0,0], 'D501C_VL_PIS' : [0,0], 'D505C_VL_ITEM' : [0,0], 'D505C_VL_BC_COFINS' : [0,0], 'D505C_VL_COFINS' : [0,0] },
        "D600" : { 'D601C_VL_ITEM': [0,0], 'D601C_VL_BC_PIS' : [0,0], 'D601C_VL_PIS' : [0,0], 'D605C_VL_ITEM' : [0,0], 'D605C_VL_BC_COFINS' : [0,0], 'D605C_VL_COFINS' : [0,0] },
        "F100" : { 'F100C_VL_OPR' : [0,0], 'F100C_VL_BC_PIS' : [0,0], 'F100C_VL_PIS' : [0,0], 'F100C_VL_BC_COFINS' : [0,0], 'F100C_VL_COFINS' : [0,0] },
        "F120" : { 'F120C_VL_BC_PIS' : [0,0], 'F120C_VL_PIS' : [0,0], 'F120C_VL_BC_COFINS' : [0,0], 'F120C_VL_COFINS' : [0,0] },
        "F130" : { 'F130C_VL_BC_PIS' : [0,0], 'F130C_VL_PIS' : [0,0], 'F130C_VL_BC_COFINS' : [0,0], 'F130C_VL_COFINS' : [0,0] },
        'F150' : { 'F150C_COD_CTA': [0, 0]},
        'F200' : { 'F211C_IND_PROC': [0, 0]},
        "F500" : { 'F500C_VL_BC_PIS' : [0,0], 'F500C_VL_PIS' : [0,0], 'F500C_VL_BC_COFINS' : [0,0], 'F500C_VL_COFINS' : [0,0] },
        'F510' : { 'F519C_IND_PROC': [0, 0]},
        'F525' : { 'F525C_COD_CTA': [0, 0]},
        'F550' : { 'F559C_IND_PROC': [0, 0]},
        'F560' : { 'F569C_IND_PROC': [0, 0]},
        'F600' : { 'F600C_IND_DEC': [0, 0]},
        'F700' : { 'F700C_INF_COMP': [0, 0]},
        'F800' : { 'F800C_PER_CRED_CIS': [0, 0]},
        'I100' : { 'I200C_INFO_COMPL': [0, 0]},
        'I200' : { 'I399C_IND_PROC': [0, 0]},
        "M100" : { 'M100C_REG': [0, 0]},
        "M105" : { 'M105C_REG': [0, 0]},
        "M110" : { 'M110C_REG': [0, 0]},
        "M115" : { 'M115C_REG': [0, 0]},
        "M200" : { 'M200C_REG': [0, 0]},
        "M205" : { 'M205C_REG': [0, 0]},
        "M210" : { 'M210C_REG': [0, 0]},
        'M211' : { 'M211C_REG': [0, 0]},
        'M215' : { 'M215C_REG': [0, 0]},
        'M220' : { 'M220C_REG': [0, 0]},
        'M225' : { 'M225C_REG': [0, 0]},
        'M230' : { 'M230C_REG': [0, 0]},
        'M300' : { 'M300C_DT_RECEB': [0, 0]},
        'M350' : { 'M350C_VL_TOT_CONT_FOL': [0, 0]},
        'M400' : { 'M410C_DESC_COMPL': [0, 0]},
        "M500" : { 'M500C_REG': [0, 0]},
        "M505" : { 'M505C_REG': [0, 0]},
        "M510" : { 'M510C_REG': [0, 0]},
        "M515" : { 'M515C_REG': [0, 0]},
        "M600" : { 'M600C_REG' : [0,0] },
        "M605" : { 'M605C_REG' : [0,0] },
        "M610" : { 'M610C_REG' : [0,0] },
        "M611" : { 'M611C_REG' : [0,0] },
        "M615" : { 'M615C_REG' : [0,0] },
        "M620" : { 'M620C_REG' : [0,0] },
        "M625" : { 'M625C_REG' : [0,0] },
        "M630" : { 'M630C_REG' : [0,0] },
        'M700' : { 'M700C_DT_RECEB': [0, 0]},
        'M800' : { 'M810C_REG': [0, 0]},
        "P100" : { 'P100C_VL_BC_CONT' : [0,0] },
        "P200" : { 'P200C_VL_TOT_AJ_ACRES' : [0,0] },
        "1010" : { '1011C_VL_PIS' : [0,0], '1011C_VL_COFINS' : [0,0] },
        '1020' : { '1020C_REG': [0, 0]},
        '1050' : { '1050C_REG': [0, 0]},
        "1100" : { '1101C_VL_OPR' : [0,0], '1101C_VL_BC_PIS' : [0,0] },
        "1200" : { '1210C_VL_OPR' : [0,0], '1210C_VL_BC_PIS' : [0,0] },
        "1300" : { '1300C_SLD_RET' : [0,0] },
        "1600" : { '1610C_VL_OPER' : [0,0], '1610C_VL_COFINS' : [0,0] }
    },
    "EFD_FISCAL" : {
        'B020' : { 'B025F_COD_SERV': [0, 0]},
        'B030' : { 'B035F_COD_SERV': [0, 0]},
        'B350' : { 'B350F_COD_INF_OBS': [0, 0]},
        'B420' : { 'B420F_COD_SERV': [0, 0]},
        'B440' : { 'B440F_VL_ISS_RT': [0, 0]},
        'B460' : { 'B460F_IND_OBR': [0, 0]},
        'B470' : { 'B470F_VL_ISS_REC_UNI': [0, 0]},
        'B500' : { 'B510F_NOME': [0, 0]},
        'C101' : { 'C101F_REG': [0, 0]},
        'C105' : { 'C105F_REG': [0, 0]},
        'C110' : { 'C111F_REG': [0, 0]},
        'C120' : { 'C120F_REG': [0, 0]},
        'C130' : { 'C130F_REG': [0, 0]},
        'C140' : { 'C141F_REG': [0, 0]},
        'C160' : { 'C160F_REG': [0, 0]},
        'C165' : { 'C165F_REG': [0, 0]},
        "C170" : { 'C170F_VL_ITEM': [0,0], 'C170F_VL_BC_ICMS' : [0,0], 'C170F_VL_ICMS' : [0,0] },
        'C180' : { 'C180F_REG': [0, 0]},
        'C181' : { 'C181F_REG': [0, 0]},
        'C185' : { 'C185F_VL_UNIT_FCP_ST_CONV_COMPL': [0, 0]},
        'C186' : { 'C186F_VL_UNIT_FCP_ST_CONV_ENTRADA': [0, 0]},
        "C190" : { 'C190F_VL_OPR' : [0,0], 'C190F_VL_BC_ICMS' : [0,0], 'C190F_VL_ICMS' : [0,0] },
        'C195' : { 'C197F_VL_OUTROS': [0, 0]},
        'C300' : { 'C330F_VL_UNIT_FCP_ST_CONV_COMPL': [0, 0]},
        "C321" : { 'C321F_REG': [0, 0]},
        'C350' : { 'C350F_REG': [0, 0]},
        "C380" : { 'C370F_VL_ITEM': [0,0] },
        'C390' : { 'C390F_VL_ICMS': [0, 0]},
        "C405" : { 'C490F_VL_OPR' : [0,0], 'C490F_VL_BC_ICMS' : [0,0], 'C490F_VL_ICMS' : [0,0] },
        "C490" : { 'C490F_VL_OPR' : [0,0], 'C490F_VL_BC_ICMS' : [0,0], 'C490F_VL_ICMS' : [0,0] },
        'C495' : { 'C495F_VL_ICMS_ST': [0, 0]},        
        "C510" : { 'C510F_REG': [0, 0]},
        "C590" : { 'C590F_REG': [0, 0]},
        "C591" : { 'C591F_REG': [0, 0]},
        "C595" : { 'C595F_REG': [0, 0]},
        "C597" : { 'C597F_REG': [0, 0]},
        "C600" : { 'C690F_VL_OPR' : [0,0], 'C690F_VL_BC_ICMS' : [0,0], 'C690F_VL_ICMS' : [0,0] },
        "C690" : { 'C690F_VL_OPR' : [0,0], 'C690F_VL_BC_ICMS' : [0,0], 'C690F_VL_ICMS' : [0,0] },
        'C700' : { 'C791F_VL_BC_ICMS_ST': [0, 0]},
        "C790" : { 'C790F_REG': [0, 0]},
        "C800" : { 'C850F_VL_OPR' : [0,0], 'C850F_VL_BC_ICMS' : [0,0], 'C850F_VL_ICMS' : [0,0] },
        "C850" : { 'C850F_REG': [0, 0]},
        "C860" : { 'C890F_VL_OPR' : [0,0], 'C890F_VL_BC_ICMS' : [0,0], 'C890F_VL_ICMS' : [0,0] },
        "C890" : { 'C890F_VL_OPR' : [0,0], 'C890F_VL_BC_ICMS' : [0,0], 'C890F_VL_ICMS' : [0,0] },
        "D101" : { 'D101F_REG': [0, 0]},
        "D110" : { 'D110F_REG': [0, 0]},
        "D120" : { 'D120F_REG': [0, 0]},
        "D130" : { 'D130F_REG': [0, 0]},
        "D140" : { 'D140F_REG': [0, 0]},
        "D150" : { 'D150F_REG': [0, 0]},
        "D160" : { 'D160F_REG': [0, 0]},
        "D161" : { 'D161F_REG': [0, 0]},
        "D162" : { 'D162F_REG': [0, 0]},
        "D170" : { 'D170F_REG': [0, 0]},
        "D180" : { 'D180F_REG': [0, 0]},
        "D190" : { 'D190F_REG': [0, 0]},
        "D195" : { 'D195F_REG': [0, 0]},
        "D197" : { 'D197F_REG': [0, 0]},
        'D300' : { 'D310F_VL_ICMS': [0, 0]},
        'D350' : { 'D390F_VL_ICMS': [0, 0]},
        'D400' : { 'D420F_VL_ICMS': [0, 0]},
        "D500" : { 'D590F_VL_OPR' : [0,0], 'D590F_VL_BC_ICMS' : [0,0], 'D590F_VL_ICMS' : [0,0] },
        "D600" : { 'D690F_VL_OPR' : [0,0], 'D690F_VL_BC_ICMS' : [0,0], 'D690F_VL_ICMS' : [0,0] },
        'D695' : { 'D697F_VL_ICMS': [0, 0]},
        'D700' : { 'D737F_VL_OUTROS': [0, 0]},
        'D750' : { 'D761F_VL_FCP_OP': [0, 0]},
        "E110" : { 'E110F_VL_ICMS_RECOLHER' : [0,0] },
        "E111" : { 'E111F_VL_AJ_APUR' : [0,0] },
        'E112' : { 'E112F_TXT_COMPL': [0, 0]},
        'E113' : { 'E113F_VL_AJ_ITEM': [0, 0]},
        "E115" : { 'E115F_VL_INF_ADIC' : [0,0] },
        "E116" : { 'E116F_VL_OR' : [0,0] },
        "E200" : { 'E200F_REG' : [0,0] },
        "E210" : { 'E210F_REG' : [0,0] },
        "E220" : { 'E220F_REG' : [0,0] },
        "E230" : { 'E230F_REG' : [0,0] },
        "E240" : { 'E240F_REG' : [0,0] },
        "E250" : { 'E250F_REG' : [0,0] },
        "E300" : { 'E316F_MES_REF' : [0,0] },
        "E500" : { 'E500F_REG' : [0,0] },
        "E510" : { 'E510F_REG' : [0,0] },
        "E520" : { 'E520F_REG' : [0,0] },
        "E530" : { 'E530F_REG' : [0,0] },
        "E531" : { 'E531F_REG' : [0,0] },
        "G125" : { 'G125F_VL_PARC_PASS' : [0,0] },
        "G126" : { 'G126F_VL_PARC_APROP' : [0,0] },
        "G130" : { 'G140F_VL_ICMS_OP_APLICADO' : [0,0] },
        "H005" : { 'H020F_BC_ICMS' : [0,0], 'H020F_VL_ICMS' : [0,0] },
        "K100" : { 'K200F_QTD' : [0,0] }
    },
    "ECF" : {
        'C050' : { 'C050ECF_REG': [0, 0]},
        'C051' : { 'C051ECF_REG': [0, 0]},
        'C100' : { 'C100ECF_REG': [0, 0]},
        'C150' : { 'C157ECF_REG': [0, 0]},
        'C350' : { 'C355ECF_REG': [0, 0]},
        'E010' : { 'E015ECF_IND_VAL_CTA': [0, 0]},
        'E020' : { 'E020ECF_COD_PB_RFB': [0, 0]},
        'E030' : { 'E355ECF_IND_VL_SLD_FIN': [0, 0]},
        "J050" : { 'J051ECF_COD_CTA_REF' : [0,0] },
        "J100" : { 'J100ECF_COD_CCUS' : [0,0] },
        "K155" : { 'K155CF_VL_SLD_INI' : [0,0], 'K155CF_VL_SLD_FIN' : [0,0]},
        "K355" : { 'K355CF_VL_SLD_FIN' : [0,0] },
        'K915' : { 'K915ECF_JUSTIFICATIVA': [0, 0]},
        'K935' : { 'K935ECF_JUSTIFICATIVA': [0, 0]},
        "L100" : { 'L100ECF_VAL_CTA_REF_INI' : [0,0], 'L100ECF_VAL_CTA_REF_FIN' : [0,0] },
        "L200" : { 'L200ECF_IND_AVAL_ESTOQ' : [0,0] },
        "L210" : { 'L210ECF_VALOR' : [0,0] },
        "L300" : { 'L300ECF_VALOR' : [0,0] },
        "M300" : { 'M312ECF_NUM_LCTO' : [0,0] },
        "M350" : { 'M362ECF_NUM_LCTO' : [0,0] },
        "M410" : { 'M410ECF_VAL_LAN_LALB_PB' : [0,0] },
        "M500" : { 'M500ECF_SD_INI_LAL' : [0,0], 'M500ECF_SD_FIM_LAL' : [0,0] },
        "M510" : { 'M510ECF_SD_INI_LAL' : [0,0], 'M510ECF_SD_FIM_LAL' : [0,0] },
        "N500" : { 'N500ECF_VALOR' : [0,0] },
        "N600" : { 'N600ECF_VALOR' : [0,0] },
        "N605" : { 'N605ECF_VALOR' : [0,0] },
        "N610" : { 'N610ECF_VALOR' : [0,0] },
        "N615" : { 'N615ECF_VL_TOTAL' : [0,0] },
        "N620" : { 'N620ECF_VALOR' : [0,0] },
        "N630" : { 'N630ECF_VALOR' : [0,0] },
        "N650" : { 'N650ECF_VALOR' : [0,0] },
        "N660" : { 'N660ECF_VALOR' : [0,0] },
        "N670" : { 'N670ECF_VALOR' : [0,0] },
        "T030" : { 'T150ECF_VALOR' : [0,0] },
        "P100" : { 'P100ECF_IND_ VAL_CTA_REF_FIN': [0, 0]},
        "P130" : { 'P130ECF_VALOR': [0, 0]},
        "P150" : { 'P150ECF_IND_ VALOR': [0, 0]},
        "P200" : { 'P200ECF_VALOR': [0, 0]},
        "P230" : { 'P230ECF_VALOR': [0, 0]},
        "P300" : { 'P300ECF_VALOR': [0, 0]},
        "P400" : { 'P400ECF_VALOR': [0, 0]},
        "P500" : { 'P500ECF_VALOR': [0, 0]},
        'Q100' : { 'Q100ECF_SLD_FIN': [0, 0]},
        'T030' : { 'T181ECF_VALOR': [0, 0]},
        'U100' : { 'U100ECF_IND_': [0, 0], 'VAL_CTA_REF_FIN': [0, 0]},
        'U150' : { 'U150ECF_IND_': [0, 0], 'VALOR': [0, 0]},
        'U180' : { 'U180ECF_VALOR': [0, 0]},
        'U182' : { 'U182ECF_VALOR': [0, 0]},
        'V020' : { 'V020ECF_IDENT_CONTA': [0, 0]},
        'V030' : { 'V030ECF_MES': [0, 0]},
        'V100' : { 'V100ECF_VALOR': [0, 0]},
        'W100' : { 'W250ECF_OBSERVAÇÃO': [0, 0]},
        'W300' : { 'W300ECF_FIM_OBSERVACAO': [0, 0]},
        'X280' : { 'X280ECF_VL_INCENTIVO': [0, 0]},
        'X291' : { 'X291ECF_VALOR': [0, 0]},
        'X292' : { 'X292ECF_VALOR': [0, 0]},
        'X300' : { 'X300ECF_TIP_MOEDA': [0, 0]},
        'X305' : { 'X305ECF_FONT_AJU': [0, 0]},
        'X310' : { 'X310ECF_COND_PES': [0, 0]},
        'X325' : { 'X325ECF_FONT_AJU': [0, 0]},
        'X330' : { 'X330ECF_COND_PES': [0, 0]},
        'X350' : { 'X350ECF_LUC_LIQ': [0, 0]},
        'X351' : { 'X351ECF_IMP_RET_BR': [0, 0]},
        'X352' : { 'X352ECF_LUC_DISP_REAL': [0, 0]},
        'X353' : { 'X353ECF_RES_PROP_REAL': [0, 0]},
        'X354' : { 'X354ECF_SALDO_RES_NEG': [0, 0]},
        'X355' : { 'X355ECF_PERCENTUAL': [0, 0]},
        'X356' : { 'X356ECF_PAT_LIQUIDO': [0, 0]},
        'X357' : { 'X357ECF_PERCENTUAL': [0, 0]},
        "X360" : { 'X360ECF_VALOR' : [0,0] },
        "X365" : { 'X365ECF_NOME_ENT' : [0,0] },
        "X366" : { 'X366ECF_VALOR' : [0,0] },
        "X370" : { 'X370ECF_DESCRICAO' : [0,0] },
        "X371" : { 'X371ECF_VALOR' : [0,0] },
        "X375" : { 'X375ECF_VALOR' : [0,0] },      
        'X390' : { 'X390ECF_VALOR': [0, 0]},
        'X400' : { 'X400ECF_VALOR': [0, 0]},
        'X410' : { 'X410ECF_IND_SERV_DISP': [0, 0]},
        'X420' : { 'X420ECF_VL_EXPL_INT': [0, 0]},
        'X430' : { 'X430ECF_VL_DIVID': [0, 0]},
        'X450' : { 'X450ECF_VL_DIVID_PJ': [0, 0]},
        'X460' : { 'X460ECF_VALOR': [0, 0]},
        'X470' : { 'X470ECF_VALOR': [0, 0]},
        'X480' : { 'X480ECF_VALOR': [0, 0]},
        'X485' : { 'X485ECF_DT_FIN_PORT_CEBAS': [0, 0]},
        'X490' : { 'X490ECF_VALOR': [0, 0]},
        'X500' : { 'X500ECF_VALOR': [0, 0]},
        'X510' : { 'X510ECF_VALOR': [0, 0]},
        'Y520' : { 'Y520ECF_VL_PERIODO': [0, 0]},
        'Y570' : { 'Y570ECF_CSLL_RET': [0, 0]},
        'Y590' : { 'Y590ECF_VL_ATUAL': [0, 0]},
        'Y600' : { 'Y600ECF_VL_IR_RET': [0, 0]},
        'Y612' : { 'Y612ECF_VL_IR_RET': [0, 0]},
        'Y620' : { 'Y620ECF_NUM_PROC_RFB': [0, 0]},
        'Y630' : { 'Y630ECF_DAT_ENCER': [0, 0]},
        'Y640' : { 'Y640ECF_VL_DECL': [0, 0]},
        'Y650' : { 'Y650ECF_VL_PART': [0, 0]},
        'Y660' : { 'Y660ECF_PERC_PAT_LIQ': [0, 0]},
        'Y672' : { 'Y672ECF_IND_AVAL_ESTOQ': [0, 0]},
        'Y680' : { 'Y681ECF_VALOR': [0, 0]},
        'Y682' : { 'Y682ECF_ACRES_PATR': [0, 0]},
        'Y720' : { 'Y720ECF_INT_ATRASO': [0, 0]},
        'Y750' : { 'Y750ECF_VALOR': [0, 0]},
        'Y800' : { 'Y800ECF_IND_FIM_RTF': [0, 0]}
    },
    "ECD" : {
        'C050': { 'C052ECD_COD_AGL': [0, 0]},
        'C150': { 'C155ECD_IND_DC_FIN_REC': [0, 0]},
        'C600': { 'C650ECD_IND_DC_CTA_FIN': [0, 0]},
        'I012': { 'I015ECD_COD_CTA_RES': [0, 0]},
        'I020': { 'I020ECD_TIPO': [0, 0]},
        'I030': { 'I030ECD_DT_EX_SOCIAL': [0, 0]},
        'I050': { 'I053ECD_NAT_SUB_CNT': [0, 0]},
        'I075': { 'I075ECD_DESCR_HIST': [0, 0]},
        'I100': { 'I100ECD_CCUS': [0, 0]},
        'I150': { 'I157ECD_IND_DC_INI': [0, 0]},
        'I200': { 'I250ECD_COD_PART': [0, 0]},
        'I300': { 'I310ECD_VAL_CREDD': [0, 0]},
        'I350': { 'I355ECD_IND_DC': [0, 0]},
        'I500': { 'I500ECD_TAM_FONTE': [0, 0]},
        'I510': { 'I510ECD_COL_CAMPO': [0, 0]},
        'I550': { 'I555ECD_RZ_CONT_TOT': [0, 0]},
        'J100': { 'J100ECD_NOTA_EXP_REF': [0, 0]},
        'J150': { 'J150ECD_NOTA_EXP_REF': [0, 0]},
        'J210': { 'J215ECD_IND_DC_FAT': [0, 0]},
        'J800': { 'J800ECD_IND_FIM_RTF': [0, 0]},
        'J801': { 'J801ECD_IND_FIM_RTF': [0, 0]},
        'J900': { 'J935ECD_COD_CVM_AUDITOR': [0, 0]},
        'K100': { 'K115ECD_PER_EVT': [0, 0]},
        'K200': { 'K300ECD_IND_VAL_CS': [0, 0]},
        'K300': { 'K315ECD_IND_VALOR': [0, 0]},
    },
    "MANAD" : {
    }
}


# TODO: Descrever finalidade do _summary_by_field
SUMMARY_BY_FIELD = {}
for sped in SUMMARY_BY_REPORT:
    SUMMARY_BY_FIELD[sped] = {}
    for reg in SUMMARY_BY_REPORT[sped]:
        for field in SUMMARY_BY_REPORT[sped][reg]:
            SUMMARY_BY_FIELD[sped][field] = SUMMARY_BY_REPORT[sped][reg][field]

