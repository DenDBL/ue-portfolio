# Плагин для генерации анимаций  

https://github.com/DenDBL/ue-portfolio/tree/029646378f67a3f46a248162936bd293e31ae365/MFA_AnimAI

Интерфейс для запросов на сервер с исскуственным интелектом для генерации анимаций для персонажей
* Создание интерфейса на PyQt
* Сетап IK Rig'ов 
* Авторетаргет анимаций от ИИ и их применение на персонажей 

# Сетап анимационного персонажа 

Настройка анимационного персонажа для стрима захвата движения в AR пространтсво в реальном времени
* Сетап AnimBP
* [Плагин-генератор ControlRig'а для коррекции блендшейпов лица на основе конфига](https://github.com/DenDBL/ue-portfolio/tree/02ae4afc0b10cdcea95df0d304ffc81bf26ac945/Facial_ControlRig_Builder)
* Сетап физ.ассета
* * Настройка костной физики ткани для примитивных движений
* * Настройка физики ушей в двух вариантах (Phys. Asset и AnimBP) и её параметризация

![](https://github.com/DenDBL/ue-portfolio/raw/master/res/tab_setup_web.mp4)

# Тестовое задание на взаимодействие персонажа с объектами окружения

https://github.com/DenDBL/ue-portfolio/tree/02ae4afc0b10cdcea95df0d304ffc81bf26ac945/Nomix_TT

* Реализация механики инвентаря
* Реализация механики взаимодействия с объектами(рычаг,вращение клапана, подбор предметов)
* Система турникетов (валидация, открытие/закрытие)
* Написан на C++

# Механика перемещения в пошаговой стратегии

https://github.com/DenDBL/ue-portfolio/tree/02ae4afc0b10cdcea95df0d304ffc81bf26ac945/TBS_Project

* Генерация сетки
* Поиск пути A*
* Механика "телепортов" между сетками
* Написан на BP

# Генерация сетки для пошаговой стратегии на C++

https://github.com/DenDBL/ue-portfolio/tree/02ae4afc0b10cdcea95df0d304ffc81bf26ac945/TBS_CPP_Source

* Ассинхронный поиск пути
* Алгоритм поиска пути в ширину
* Изменение состояни в зависимости от выставленного на клетки объекта
* Динамические преграды

```cpp
TArray<FIntPoint> Acpp_PathFinding::FindPath(const FIntPoint& Start, const FIntPoint& End, const TMap<FIntPoint, bool>& Map)
{
    TArray<FIntPoint> Path;
    TMap<FIntPoint, int32> GScore;  
    TMap<FIntPoint, int32> FScore;  
    TMap<FIntPoint, FIntPoint> CameFrom;  
    TArray<FIntPoint> OpenSet;  

    GScore.Add(Start, 0);  
    FScore.Add(Start, (End - Start).Size());  
    OpenSet.Add(Start);  

    while (OpenSet.Num() > 0)
    {
        
        int32 MinIndex = 0;
        for (int32 i = 0; i < OpenSet.Num(); i++)
        {
            if (FScore.FindRef(OpenSet[i]) < FScore.FindRef(OpenSet[MinIndex]))
            {
                MinIndex = i;
            }
        }
        FIntPoint Current = OpenSet[MinIndex];

        
        if (Current == End)
        {
            Path.Add(Current);
            while (CameFrom.Contains(Current))
            {
                Current = CameFrom[Current];
                Path.Add(Current);
            }
            Algo::Reverse(Path);
            //Path.Reverse();  
            return Path;
        }

        OpenSet.RemoveAt(MinIndex);  

        TArray<FIntPoint> Neighbors;
        GetNeighbors(Current, Map, Neighbors);  
        for (const FIntPoint& Neighbor : Neighbors)
        {
            const int32 TentativeGScore = GScore.FindRef(Current) + 1;  

            if (!GScore.Contains(Neighbor) || TentativeGScore < GScore.FindRef(Neighbor))
            {
                CameFrom.Add(Neighbor, Current);  
                GScore.Add(Neighbor, TentativeGScore);  
                FScore.Add(Neighbor, TentativeGScore + (End - Neighbor).Size());  

                if (!OpenSet.Contains(Neighbor))
                {
                    OpenSet.Add(Neighbor);  
                }
            }
        }
    }

    return Path;  
}
```


