// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/DataTable.h"
#include "Engine/World.h"
#include "Components/ChildActorComponent.h" 
#include "Kismet/GameplayStatics.h"
#include "CPP_Utility.h"
#include "CPP_GridVisual.h"

#include "CPP_Grid.generated.h"







UCLASS()
class TBS_PROJECT_API ACPP_Grid : public AActor
{
	GENERATED_BODY()
	
	UPROPERTY(EditAnywhere, Category = "Grid")
		class ACPP_GridVisual* gridVisual = nullptr;

public:	
	// Sets default values for this actor's properties
	ACPP_Grid();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	

	virtual void PostInitializeComponents() override;

	FVector gridCenterLocation = GetActorLocation();
	FVector gridBottomLeftCornerLocation;
	UPROPERTY(BlueprintReadOnly)
	TMap <FIntPoint, FTileData> gridTiles;

	
	
	




	FVector FindCenterLocation();
	FVector FindBottomLeftCornerLocation();
	void AddGridTile(FTileData data);
	void DestroyGrid();

	FTileGraphPositionPair TraceForTileBelow(FIntPoint index, float rayLength);

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid")
		FIntPoint gridSize = { 10,10 };

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid")
		FVector tileSize = { 100,100,100 };

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid")
		class UDataTable* gridShapeDataTable = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Debug")
		bool debug = false;

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void GenerateGrid();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Grid")
		class ACPP_GridVisual* GetGridVisualCA();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Grid")
		TMap <FIntPoint, FTileData> GetGridTiles();

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void LogTilesPostion();

	UFUNCTION(BlueprintCallable, Category = "Grid")
		TileType GroundTracing(FVector location, FIntPoint index);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void ModifierTracing(FVector location, FIntPoint index);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Components")
		class USceneComponent* SceneRoot = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Components")
		class UChildActorComponent* CA_GridVisual = nullptr;

	

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid")
		bool groundTrace = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid")
		bool modifierTrace = false;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Grid")
		FVector GetBottomLeftCornerLocation() { return gridBottomLeftCornerLocation; };

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Grid")
		FVector GetCenterLocation() { return gridCenterLocation; };

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void SetTileType(FIntPoint index, TileType type);
	
	UFUNCTION(BlueprintCallable, Category = "Grid")
		void AddLeadTo(FIntPoint index, FTileGraphPositionPair toTile);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void AddUnableMoveTo(FIntPoint index, TileDirection direction);

	UFUNCTION(BlueprintCallable, Category = "Grid")
		void TraceForGridBelow();

	
};
