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

![ears_setup_web](https://github.com/DenDBL/ue-portfolio/blob/master/res/ears_setup_web.gif?raw=true)
![tab_setup_web](https://github.com/DenDBL/ue-portfolio/blob/master/res/tab_setup_web.gif?raw=true)

# Тестовое задание на взаимодействие персонажа с объектами окружения

https://github.com/DenDBL/ue-portfolio/tree/02ae4afc0b10cdcea95df0d304ffc81bf26ac945/Nomix_TT

* Реализация механики инвентаря
* Реализация механики взаимодействия с объектами(рычаг,вращение клапана, подбор предметов)
* Система турникетов (валидация, открытие/закрытие)
* Написан на C++

```cpp
#include "CPP_InventoryComponent.h"
#include "CPP_GameMode.h"
// Sets default values for this component's properties
UCPP_InventoryComponent::UCPP_InventoryComponent()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	InitSlots();
}


// Called when the game starts
void UCPP_InventoryComponent::BeginPlay()
{
	Super::BeginPlay();

	ACPP_GameMode* CurrentGameMode = Cast<ACPP_GameMode>(GetWorld()->GetAuthGameMode());

	if (CurrentGameMode)
		slotsCount = CurrentGameMode->numberOfSlots;
	
	InitSlots();
	
}


// Called every frame
void UCPP_InventoryComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// ...
}

void UCPP_InventoryComponent::InitSlots()
{
	if (slotsCount == 0)
		return;

	slots.Empty();

	for (int i = 0; i < slotsCount; i++) {
		slots.Add(nullptr);
	}
}

void UCPP_InventoryComponent::AddItemToInventory(AActor* item)
{
	if (slots.Num() == 0)
		return;

	for (int i = 0; i < slotsCount ;i++) {
		if (!slots[i]) {
			slots[i] = item;
			UpdateSelectedSlot();
			break;
		}
	}
	
}

void UCPP_InventoryComponent::UpdateSelectedSlot()
{
	for (auto& slot : slots) {
		if (slot) {
			slot->SetActorHiddenInGame(true);
			//slot->SetActorEnableCollision(false);
		}
	}

	AActor* selectedActor = slots[selectedSlot];
	if (selectedActor) {
		selectedActor->SetActorHiddenInGame(false);
	}

}

void UCPP_InventoryComponent::SelectSlot(int number)
{	
	number = FMath::Clamp(number, 0, slotsCount - 1);

	selectedSlot = number;
	UpdateSelectedSlot();
}

AActor* UCPP_InventoryComponent::GetSelectedItem()
{
	return slots[selectedSlot];
}
```

# Механика перемещения в пошаговой стратегии

https://github.com/DenDBL/ue-portfolio/tree/02ae4afc0b10cdcea95df0d304ffc81bf26ac945/TBS_Project

* Генерация сетки
* Поиск пути A*
* Механика "телепортов" между сетками
* Написан на BP

https://youtu.be/lA6sjCvlY0g?si=Y3QrVVCgtQtF-GcZ

# Генерация сетки для пошаговой стратегии на C++

https://github.com/DenDBL/ue-portfolio/tree/02ae4afc0b10cdcea95df0d304ffc81bf26ac945/TBS_CPP_Source

* Ассинхронный поиск пути
* Алгоритм поиска пути в ширину
* Изменение состояни в зависимости от выставленного на клетки объекта
* Динамические преграды

https://youtu.be/CglKwVdOMgs?si=G27rPcdmO0_ulQ0y

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


