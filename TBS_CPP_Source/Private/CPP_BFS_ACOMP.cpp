// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_BFS_ACOMP.h"
#include "CPP_Grid.h"
// Sets default values for this component's properties
UCPP_BFS_ACOMP::UCPP_BFS_ACOMP()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = false;

	

	// ...
}


// Called when the game starts
void UCPP_BFS_ACOMP::BeginPlay()
{
	Super::BeginPlay();

	// ...
	
}




// Called every frame
void UCPP_BFS_ACOMP::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// ...
}

int32 UCPP_BFS_ACOMP::GetDistance(FTileGraphPositionPair inTile) {

	for (auto& distance : distances) {
		if (distance.tile.grid == inTile.grid && distance.tile.index == inTile.index)
			return distance.distance;
	}
	return int32();
}
TArray<FTileGraphPositionPair> UCPP_BFS_ACOMP::GetPath(FTileGraphPositionPair inTile) {

	for (auto& path : paths) {
		if (path.tile.grid == inTile.grid && path.tile.index == inTile.index)
			return path.path;
	}
	return TArray<FTileGraphPositionPair>();
}


void UCPP_BFS_ACOMP::GetReachableTilesUtil(FTileGraphPositionPair tile)
{	

	if (!tile.grid)
		return;

	queue.Enqueue(tile);
	visited.Add(tile);

	distances.Add(FDistanceToTile(tile, 0));


	while (!queue.IsEmpty()) {
		FTileGraphPositionPair currentTile;
		queue.Dequeue(currentTile);

		int32 currentDist = GetDistance(currentTile);

		if (currentDist >= maxDistance)
			return;

		for (auto& neighbourTile : GetTileReachableNeighbours(currentTile)) {
			if (visited.Contains(neighbourTile))
				continue;

			visited.Add(neighbourTile);
			queue.Enqueue(neighbourTile);

			distances.Add(FDistanceToTile(neighbourTile, currentDist + 1));
			
			TArray<FTileGraphPositionPair> nextPath = GetPath(currentTile);
			nextPath.Add(neighbourTile);
			paths.Add(FPathToTile(neighbourTile,nextPath));


			
		}


	}


}

TArray<FTileGraphPositionPair> UCPP_BFS_ACOMP::GetTileReachableNeighbours(FTileGraphPositionPair tile)
{
	TArray<FTileGraphPositionPair> returnTiles;
	FTileData tileInfo = tile.grid->GetGridTiles().FindRef(tile.index);
	
	returnTiles.Append(GetTileGridNeighbours(tile));

	returnTiles.Append(tileInfo.leadTo);

	return returnTiles;
}

TArray<FTileGraphPositionPair> UCPP_BFS_ACOMP::GetTileGridNeighbours(FTileGraphPositionPair tile)
{
	TMap<FIntPoint, FTileData> gridTiles = tile.grid->GetGridTiles();
	TArray<FTileGraphPositionPair> returnTiles;

	FTileGraphPositionPair offset = tile;
	
	if (CanMoveTo(gridTiles.FindRef(tile.index), gridTiles, TileDirection::Forward) ){
		offset.index = tile.index + FIntPoint(0, 1);
		returnTiles.Add(offset);
	}
	if (CanMoveTo(gridTiles.FindRef(tile.index), gridTiles, TileDirection::Right)) {
		offset.index = tile.index + FIntPoint(1, 0);
		returnTiles.Add(offset);
	}
	if (CanMoveTo(gridTiles.FindRef(tile.index), gridTiles, TileDirection::Backward)) {
		offset.index = tile.index + FIntPoint(0, -1);
		returnTiles.Add(offset);
	}
	if (CanMoveTo(gridTiles.FindRef(tile.index), gridTiles, TileDirection::Left)) {
		offset.index = tile.index + FIntPoint(-1, 0);
		returnTiles.Add(offset);
	}

	return returnTiles;
}

bool UCPP_BFS_ACOMP::CanMoveTo(FTileData tileData, TMap<FIntPoint, FTileData> gridTiles,TileDirection direction)
{	
	if(tileData.unableMoveTo.Contains(direction))
		return false;

	FIntPoint offset = tileData.index;
	switch (direction)
	{
	case TileDirection::Forward:
		offset += FIntPoint(0, 1);
		break;
	case TileDirection::Right:
		offset += FIntPoint(1, 0);
		break;
	case TileDirection::Backward:
		offset += FIntPoint(0, -1);
		break;
	case TileDirection::Left:
		offset += FIntPoint(-1, 0);
		break;
	default:
		offset += FIntPoint(0, 0);
		break;
	}

	if (!gridTiles.Contains(offset))
		return false;

	if (!UCPP_Utility::IsTileWalkable(tileData))
		return false;
	
	return true;
}


TArray<FPathToTile> UCPP_BFS_ACOMP::GetReachableTiles(
	FTileGraphPositionPair tile,
	int32 maxDist)
{
	visited.Empty();
	queue.Empty();
	distances.Empty();
	paths.Empty();
	maxDistance = maxDist;


	TArray<FTileGraphPositionPair> beginPath;
	beginPath.Add(tile);
	paths.Add(FPathToTile(tile, beginPath));
	
	GetReachableTilesUtil(tile);

	return paths;
}

void UCPP_BFS_ACOMP::FindReachableTilesAsync(FTileGraphPositionPair tile, int32 maxDist)
{
	if (!isThreadBusy) {
		isThreadBusy = true;
		Async(EAsyncExecution::Thread, [&]() {
			GetReachableTiles(tile, maxDist);
			FFunctionGraphTask::CreateAndDispatchWhenReady([this]() {
				OnPathCalcEnd.Broadcast(paths);
				isThreadBusy = false;
				}, TStatId(), nullptr, ENamedThreads::GameThread);
			});
	}
}

