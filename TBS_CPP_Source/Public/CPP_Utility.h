// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CollisionQueryParams.h"
#include "Kismet/GameplayStatics.h"
#include "CPP_Utility.generated.h"

class ACPP_Grid;

UENUM(BlueprintType)
enum class TileType : uint8
{
	None,
	Default,
	Obstacle
};

UENUM(BlueprintType)
enum class TileDirection : uint8
	{
		Forward,
		Right,
		Backward,
		Left
	};

USTRUCT(BlueprintType)
struct FGridShapeData : public FTableRowBase
{
	GENERATED_BODY()

		UPROPERTY(EditAnywhere, BlueprintReadWrite)
		FVector MeshSize;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		UStaticMesh* Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		UMaterialInstance* MeshMaterial;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		UStaticMesh* FlatMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		UMaterialInstance* FlatBorderMaterial;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		UMaterialInstance* FlatFilledMaterial;
};

USTRUCT(BlueprintType)
struct FTileGraphPositionPair
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FIntPoint index = FIntPoint();
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	ACPP_Grid* grid =  nullptr;

	bool operator==(const FTileGraphPositionPair& Other) const
	{
		return index == Other.index && grid == Other.grid;
	}
	
	FTileGraphPositionPair() {};
	FTileGraphPositionPair(FIntPoint inIndex, ACPP_Grid* inGrid) : index(inIndex), grid(inGrid) {};

};

USTRUCT(BlueprintType)
struct FPathToTile
{
	GENERATED_BODY()
		UPROPERTY(EditAnywhere, BlueprintReadWrite)
		FTileGraphPositionPair tile;

		UPROPERTY(EditAnywhere, BlueprintReadWrite)
		TArray<FTileGraphPositionPair> path;

		FPathToTile() {};
		FPathToTile(FTileGraphPositionPair inTile, TArray<FTileGraphPositionPair> inPath): tile(inTile), path(inPath) {};
};

USTRUCT(BlueprintType)
struct FDistanceToTile
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		FTileGraphPositionPair tile;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		int32 distance;

	FDistanceToTile() {};

	FDistanceToTile(FTileGraphPositionPair inTile, uint32 inDistance) :tile(inTile), distance(inDistance) {};

};

USTRUCT(BlueprintType)
struct FTileData
{
	GENERATED_BODY()
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FIntPoint index;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FTransform transform;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TileType type = TileType::None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<FTileGraphPositionPair> leadTo; //Дополнительные доступные клектки для пермещения в формате Индекс клетки Сетка клетки

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<TileDirection> unableMoveTo; //Направления клектки, на которые с этой клетки нельзя перемещаться 
};


USTRUCT()
struct FTraceRespond {
	GENERATED_BODY()

	bool isHit;
	FHitResult HitResult;
};

USTRUCT()
struct FMultiTraceRespond {
	GENERATED_BODY()

	bool isHit;
	TArray<FHitResult> HitsResult;
};

UCLASS()
class TBS_PROJECT_API UCPP_Utility : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UCPP_Utility();
	~UCPP_Utility();
	/** Привзяка позиции к сетке*/
	static FVector SnapPositionToGrid(FVector position,FVector grid);

	/** Четность числа*/
	static bool IsEven(float number);
	
	static FTraceRespond SweepSingleSphereByChannel(UWorld* World, FVector StartLocation, FVector EndLocation,
		float Radius, ECollisionChannel CollisionChannel);

	static FMultiTraceRespond SweepMultiSphereByChannel(UWorld* World, FVector StartLocation, FVector EndLocation,
		float Radius, ECollisionChannel CollisionChannel);


	
	static bool IsTileWalkable(FTileData data);

	UFUNCTION(BlueprintCallable, Category = "Grid")
	static FIntPoint GetTileByLocationOnGrid(ACPP_Grid* grid, FVector location);


	
};
