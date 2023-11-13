// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_Utility.h"
#include "Engine/World.h"
#include "CPP_Grid.h"

UCPP_Utility::UCPP_Utility()
{
}

UCPP_Utility::~UCPP_Utility()
{
}

FVector UCPP_Utility::SnapPositionToGrid(FVector position, FVector grid)
{

	FVector snappedPosition;

	snappedPosition.X = FMath::GridSnap(position.X,grid.X);
	snappedPosition.Y = FMath::GridSnap(position.Y, grid.Y);
	snappedPosition.Z = FMath::GridSnap(position.Z, grid.Z);


	return snappedPosition;
}

bool UCPP_Utility::IsEven(float number)
{
	return FMath::IsNearlyZero(FMath::Fmod(number, 2.0f));
	
}

FTraceRespond UCPP_Utility::SweepSingleSphereByChannel(UWorld* World,FVector StartLocation,
    FVector EndLocation, float Radius, ECollisionChannel CollisionChannel)
{   

    FTraceRespond respond;

    // Установка параметров запроса трассировки
    FCollisionQueryParams TraceParams;
    TraceParams.bTraceComplex = false;
    

    // Результат трассировки
    FHitResult HitResult;
    
    // Трассировка перемещающейся формы по указанным параметрам
    bool bHit = World->SweepSingleByChannel(
        HitResult,
        StartLocation,
        EndLocation,
        FQuat::Identity,
        CollisionChannel,
        FCollisionShape::MakeSphere(Radius),
        TraceParams,
        FCollisionResponseParams()

    );

    respond.isHit = bHit;
    respond.HitResult = HitResult;

    return respond;
}

FMultiTraceRespond UCPP_Utility::SweepMultiSphereByChannel(UWorld* World, FVector StartLocation, FVector EndLocation, float Radius, ECollisionChannel CollisionChannel)
{

    FMultiTraceRespond respond;

    // Установка параметров запроса трассировки
    FCollisionQueryParams TraceParams;
    TraceParams.bTraceComplex = false;


    // Результат трассировки
    TArray<FHitResult> HitsResult;

    // Трассировка перемещающейся формы по указанным параметрам
    bool bHit = World->SweepMultiByChannel(
        HitsResult,
        StartLocation,
        EndLocation,
        FQuat::Identity,
        CollisionChannel,
        FCollisionShape::MakeSphere(Radius),
        TraceParams,
        FCollisionResponseParams()

    );

    respond.isHit = bHit;
    respond.HitsResult = HitsResult;

    
    return respond;
}

bool UCPP_Utility::IsTileWalkable(FTileData data)
{
    TArray<TileType> notWalkableTypes = { TileType::None,TileType::Obstacle };
    
    return !notWalkableTypes.Contains(data.type);
}

FIntPoint UCPP_Utility::GetTileByLocationOnGrid(ACPP_Grid* grid, FVector location)
{
    FVector snappedPos = SnapPositionToGrid(location - grid->GetBottomLeftCornerLocation(), grid->tileSize);
    return FIntPoint(snappedPos.X / grid->tileSize.X, snappedPos.Y / grid->tileSize.Y);
}

