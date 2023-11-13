// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CPP_Utility.h"


#include "CPP_BFS_ACOMP.generated.h"

UDELEGATE(BlueprintAuthorityOnly)
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPathCalcEndDelegate, TArray<FPathToTile>, Paths);

USTRUCT(BlueprintType)
struct FPathToTileNoIndex
{	
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		TArray<FTileGraphPositionPair> path;

	FPathToTileNoIndex() {};

	FPathToTileNoIndex(TArray<FTileGraphPositionPair> inPath) {
		path = inPath;
	};
};

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class TBS_PROJECT_API UCPP_BFS_ACOMP : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UCPP_BFS_ACOMP();
	UPROPERTY(BlueprintAssignable, Category = "MyEvent")
		FOnPathCalcEndDelegate OnPathCalcEnd;

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

	
	TArray<FPathToTile> paths;

	

	TArray<FTileGraphPositionPair> visited;

	TQueue<FTileGraphPositionPair> queue;

	TArray<FDistanceToTile> distances;

	bool isThreadBusy = false;

	int32 maxDistance;

	void GetReachableTilesUtil(FTileGraphPositionPair tile);

	TArray<FTileGraphPositionPair> GetTileReachableNeighbours(FTileGraphPositionPair tile);

	TArray<FTileGraphPositionPair> GetTileGridNeighbours(FTileGraphPositionPair tile);

	bool CanMoveTo(FTileData tileData, TMap<FIntPoint, FTileData> gridTiles, TileDirection direction);

	int32 GetDistance(FTileGraphPositionPair inTile);

	TArray<FTileGraphPositionPair> GetPath(FTileGraphPositionPair inTile);

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	
	UFUNCTION(BlueprintCallable)
		TArray<FPathToTile> GetReachableTiles(FTileGraphPositionPair tile, int32 maxDist);

	UFUNCTION(BlueprintCallable)
		void FindReachableTilesAsync(FTileGraphPositionPair tile, int32 maxDist);
		
};
