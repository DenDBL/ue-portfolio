// Fill out your copyright notice in the Description page of Project Settings.


#include "cpp_PathFinding.h"


#include "Containers/UnrealString.h"
#include "Math/IntPoint.h"
#include "Algo/Reverse.h"


struct PathNode
{
	FIntPoint Position;  // ������� ����
	int32 Cost;          // ��������� ���� �� ������� ����
	int32 Heuristic;     // ��������� ���������� �� ����
};


// Sets default values
Acpp_PathFinding::Acpp_PathFinding()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = false;

}

// Called when the game starts or when spawned
void Acpp_PathFinding::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void Acpp_PathFinding::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

// ������� ����������� �������
void GetNeighbors(const FIntPoint& Current, const TMap<FIntPoint, bool>& Map, TArray<FIntPoint>& Neighbors)
{
    const FIntPoint Left(Current.X - 1, Current.Y);
    const FIntPoint Right(Current.X + 1, Current.Y);
    const FIntPoint Up(Current.X, Current.Y - 1);
    const FIntPoint Down(Current.X, Current.Y + 1);

    // ���������, �������� �� ������ ����������� ��������
    if (Map.FindRef(Left))
    {
        Neighbors.Add(Left);
    }
    if (Map.FindRef(Right))
    {
        Neighbors.Add(Right);
    }
    if (Map.FindRef(Up))
    {
        Neighbors.Add(Up);
    }
    if (Map.FindRef(Down))
    {
        Neighbors.Add(Down);
    }
}

// ������� ���������� ����
TArray<FIntPoint> Acpp_PathFinding::FindPath(const FIntPoint& Start, const FIntPoint& End, const TMap<FIntPoint, bool>& Map)
{
    TArray<FIntPoint> Path;
    TMap<FIntPoint, int32> GScore;  // ����� ��� �������� ��������� ���� �� ������ �� ������ ������
    TMap<FIntPoint, int32> FScore;  // ����� ��� �������� ��������� ��������� ���� �� ������ �� �������� ������ ����� ������ ������
    TMap<FIntPoint, FIntPoint> CameFrom;  // ����� ��� �������� ������������ ������, ����� ������������ ����
    TArray<FIntPoint> OpenSet;  // �������� ������ ��� �������� ������, ������� ����� ���������

    GScore.Add(Start, 0);  // ��������� ������ ����� ��������� 0
    FScore.Add(Start, (End - Start).Size());  // ��������� ��������� ��� ��������� ������
    OpenSet.Add(Start);  // ��������� ��������� ������ � �������� ������

    while (OpenSet.Num() > 0)
    {
        // ������� ������ � ���������� ��������� ���������� FScore
        int32 MinIndex = 0;
        for (int32 i = 0; i < OpenSet.Num(); i++)
        {
            if (FScore.FindRef(OpenSet[i]) < FScore.FindRef(OpenSet[MinIndex]))
            {
                MinIndex = i;
            }
        }
        FIntPoint Current = OpenSet[MinIndex];

        // ���� �� �������� �������� ������, ���������� ��������� ����
        if (Current == End)
        {
            Path.Add(Current);
            while (CameFrom.Contains(Current))
            {
                Current = CameFrom[Current];
                Path.Add(Current);
            }
            Algo::Reverse(Path);
            //Path.Reverse();  // �������������� ����,
            return Path;
        }

        OpenSet.RemoveAt(MinIndex);  // ������� ������� ������ �� ��������� ������

        TArray<FIntPoint> Neighbors;
        GetNeighbors(Current, Map, Neighbors);  // �������� ������� ������� ������
        for (const FIntPoint& Neighbor : Neighbors)
        {
            const int32 TentativeGScore = GScore.FindRef(Current) + 1;  // �������������� ��������� ���� �� �������� ������ (1, ��� ��� ��������� ������ ����������)

            // ���� �������� ������ ��� �� �������� ��� ����� ���� �� ��� ����� ����������
            if (!GScore.Contains(Neighbor) || TentativeGScore < GScore.FindRef(Neighbor))
            {
                CameFrom.Add(Neighbor, Current);  // ������������� ������� ������ ��� ������������ ��� ��������
                GScore.Add(Neighbor, TentativeGScore);  // ��������� ��������� ���� �� �������� ������
                FScore.Add(Neighbor, TentativeGScore + (End - Neighbor).Size());  // ��������� ��������� ��������� ���� ����� �������� ������ �� ��������

                if (!OpenSet.Contains(Neighbor))
                {
                    OpenSet.Add(Neighbor);  // ��������� �������� ������ � �������� ������ ��� ���������� ��������
                }
            }
        }
    }

    return Path;  // ���� ���� �� ������, ���������� ������ ������
}




