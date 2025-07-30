class PeterJuice:
    """
    class PeterJuice คือ
    ข้อมูลที่เกี่ยวข้องกับ PeterJuice
    ประกอบด้วยชื่อ Youtube aboutme
    art
    

    Demonstate
    #--------------------
    Peter = PeterJuice()
    Peter.show_name()
    Peter.show_YT()
    Peter.aboutme()
    Peter.show_art()
    #--------------------
    """
    def __init__(self):
        self.name = 'Peter'
        self.youtube = 'https://www.youtube.com/@redcometz6205'

    def show_name(self):
        print(f'สวัสดีผมชื่อ {self.name}')

    def show_YT(self):
        print('https://www.youtube.com/@redcometz6205')

    def aboutme(self):
        text = '''
    ----------------------------------------------------
    สวัสดีครับ ผมเป็นมือใหม่ในวงการ Python ครับยินดีที่ได้รู้จักครับ
    ผมมีความฝันอยากสร้างโปรแกรมมาตั้งแต่ปี2แล้วครับและตอนนี้เรียน
    จบแล้วพึ่งได้มาเริ่มต้นครับ ผมเป็นคนชอบหนังสือครับการอ่านก็เหมือน
    กับการเรียนรู้ประสบการณ์คนอื่นที่เขาอาจใช้เวลาหลายปีในการตกผลึก
    มาเขียนหนังสือแต่เราสามารถเรียนรู้จากเขาได้ในไม่กี่ชั่วโมง
    ---------------------------------------------------- '''    
        print(text)

    def show_art(self):
        text = '''
        .--.                   .---.
    .---|__|           .-.     |~~~|
    .--|===|--|_          |_|     |~~~|--.
    |  |===|  |'\     .---!~|  .--|   |--|
    |%%|   |  |.'\    |===| |--|%%|   |  |
    |%%|   |  |\.'\   |   | |__|  |   |  |
    |  |   |  | \  \  |===| |==|  |   |  |
    |  |   |__|  \.'\ |   |_|__|  |~~~|__|
    |  |===|--|   \.'\|===|~|--|%%|~~~|--|
    ^--^---'--^    `-'`---^-^--^--^---'--'
'''
        print(text)

if __name__ == '__main__':
    Peter = PeterJuice()
    Peter.show_name()
    Peter.show_YT()
    Peter.aboutme()
    Peter.show_art()