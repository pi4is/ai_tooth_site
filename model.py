from ultralytics import YOLO
import os

def analitic(img_path):
    print(img_path)
    model = YOLO("best.pt")
    result = model.predict(source=img_path, show=False, save=True, conf=0.6, project="path/img_analytics_users")

    names = model.names
    boxes = result[0].boxes
    names_img = []

    for name in boxes.cls:
        if names_img in names[int(name)]:
            pass
        else:
            names_img.append(names[int(name)])
    listed = os.listdir("path/img_analytics_users")
    return names_img, listed

class img_analytics:
    def __init__(self):
        self.model = YOLO("best.pt")
        print("$$$ Model load! $$$")
    def analytics(self, img_path):
        print("$$$ Start Analytic from: ",img_path, " $$$")
        result = self.model.predict(source=img_path, show=False, save=True, conf=0.6, project="static/img_analytics_users")

        names = self.model.names
        boxes = result[0].boxes
        names_img = []

        for name in boxes.cls:
            if names[int(name)] not in names_img:
                names_img.append(names[int(name)])
        listed = os.listdir("static/img_analytics_users")

        analysis = ""
        if len(names_img) == 0:
            analysis += "Проблем с зубами не найдено"
        else:
            for anal in names_img:
                if anal == "caries":
                    analysis += "У вас найден кариес. В данном случае необходим визит к стомотологу, где вам смогут его убарть. Визит нужен в ближайшее время, так как если запустить кариес, он может дойти до пульпита"
                elif anal == "white_spot":
                    analysis += "У вас найдены белые пятна на зубах. В данном случает необходима хорошая чистка зубов, так же сещуствуют специальные пасты, которые удаляют кариес в стадии белого пятна. Если чистка не помога, нужен визит к стомотологу, где вам удалят белые пятна. Белое пятно - это первая стадия развития кариеса на зубах"
                elif anal == "errozian":
                    analysis += "У вас найдена эрозия эмали, в данном случае необходим визит к стомотологу."
                elif anal == "tartar":
                    analysis += "У вас найден зубной камень или же налет на зубах, необходима чистка зубов, если зубной камень остался - необходим визит к стомотологу"

        listes = []
        if len(listed) > 1:
            for list in listed:
                print(list)
                if list.split("predict")[1] != '':
                    listes.append(int(list.split("predict")[1]))
            listes = sorted(listes)
            return names_img, "predict" + str(listes[-1]) + "/" + img_path.split("/")[-1], analysis
        else:
            return names_img, "predict/"+img_path.split("/")[-1], analysis