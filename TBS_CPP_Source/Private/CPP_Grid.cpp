// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_Grid.h"
#include "CPP_GridModifier.h"
#include "Engine/StaticMeshActor.h"

// Sets default values
ACPP_Grid::ACPP_Grid()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = false;

    
    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("DefaultSceneRoot"));
    SetRootComponent(SceneRoot);
   
    

   // gridVisual = GetWorld()->SpawnActor<ACPP_GridVisual>(ACPP_GridVisual::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator);
   // gridVisual->AttachToComponent(RootComponent, FAttachmentTransformRules::KeepRelativeTransform);
    
    
     CA_GridVisual = CreateDefaultSubobject<UChildActorComponent>(TEXT("Grid Visual"));
     //CA_GridVisual->ReregisterComponent();
     //UChildActorComponent*  CA_GridVisual = NewObject<UChildActorComponent>(this, TEXT("ChildActorComponentName"));
     CA_GridVisual->SetEditorTreeViewVisualizationMode(EChildActorComponentTreeViewVisualizationMode::ChildActorOnly);
     CA_GridVisual->SetupAttachment(SceneRoot);
     CA_GridVisual->SetChildActorClass(ACPP_GridVisual::StaticClass());
     

   
}


void ACPP_Grid::PostInitializeComponents() {
    Super::PostInitializeComponents();
    GenerateGrid();
}

// Called when the game starts or when spawned
void ACPP_Grid::BeginPlay()
{
	Super::BeginPlay();
    

}

// Called every frame
void ACPP_Grid::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

void ACPP_Grid::GenerateGrid()
{
    // Âû÷èñëåíèå îáùåãî ðàçìåðà ñåòêè
    //FVector gridSize = FVector(gridTileSize.X * tileCount.X, gridTileSize.Y * tileCount.Y, gridTileSize.Z * tileCount.Y);

    // Âû÷èñëåíèå íà÷àëüíîé ïîçèöèè ñåòêè
    //FVector gridOrigin = centerLocation - gridSize * 0.5f;
    if (!CA_GridVisual) {
        UE_LOG(LogTemp, Log, TEXT("НЕТ ДОЧЕРНЕГО КОМПОНЕНТА"));
        return;

    }
    if (!GetGridVisualCA()) {
        UE_LOG(LogTemp, Log, TEXT("Нет дочернего актора"));
        return;

    }

    DestroyGrid();

    GetGridVisualCA()->InitGridVisuals(gridShapeDataTable,this);

    gridCenterLocation.X = FindCenterLocation().X;
    gridCenterLocation.Y = FindCenterLocation().Y;
    gridCenterLocation.Z = GetActorLocation().Z;
    gridBottomLeftCornerLocation = FindBottomLeftCornerLocation();

    FGridShapeData* DataRow;

    if (gridShapeDataTable)
        DataRow = gridShapeDataTable->FindRow<FGridShapeData>(FName("Square"), "Получение строки из таблицы данных GridShapeData");
    else
        return;

    
    FTransform tileTransform(FRotator(0.0f, 0.0f, 0.0f), FVector(0.0f, 0.0f, 0.0f), tileSize / DataRow->MeshSize);


    // Ãåíåðàöèÿ ñåòêè
    for (int32 X = 0; X < gridSize.X; ++X)
    {
        for (int32 Y = 0; Y < gridSize.Y; ++Y)
        {
            FVector tilePosition = gridBottomLeftCornerLocation + (tileSize * FVector(X, Y, 0.0));
            tileTransform.SetLocation(tilePosition);

            FTileData tileData;
            tileData.index = { X,Y };
            tileData.transform = tileTransform;
            
            //DrawDebugSphere(GetWorld(), tilePosition, 50.f, 6, FColor(255, 0, 0), false, 1.0f, 0, 2.0f);

            
            tileData.type = TileType::Default;

            if (groundTrace)
                tileData.type = GroundTracing(tilePosition, FIntPoint(X, Y));
             /*if ((tileData.type = TileTracing(tilePosition, FIntPoint(X, Y))) != TileType::None) {
                    DrawDebugBox(GetWorld(), tilePosition, FVector(50.0f, 50.0f, 50.0f), FColor(255, 0, 0),
                        false, 5.0f, 0, 10.0f);
                }
                else
                    DrawDebugBox(GetWorld(), tilePosition, FVector(50.0f, 50.0f, 50.0f), FColor(0, 255, 0),
                        false, 5.0f, 0, 10.0f);
            else
                tileData.type = TileType::Default;*/

            AddGridTile(tileData);

            if (modifierTrace)
                ModifierTracing(tilePosition, FIntPoint(X, Y));

            
        }
    }
    //TraceForGridBelow();
}

ACPP_GridVisual* ACPP_Grid::GetGridVisualCA()
{   
    if(CA_GridVisual)
       return Cast<ACPP_GridVisual>(CA_GridVisual->GetChildActor());
    else {
        UE_LOG(LogTemp, Log, TEXT("Не удалось получить GetChildActor"));
        return nullptr;
    }
}

void ACPP_Grid::DestroyGrid() {
    gridTiles.Empty();
    GetGridVisualCA()->ClearInstances();
}

FTileGraphPositionPair ACPP_Grid::TraceForTileBelow(FIntPoint index, float rayLength)
{
    FVector StartLocation = gridTiles.Find(index)->transform.GetLocation();
    FVector EndLocation = StartLocation - FVector(0.f,0.f,rayLength);

    FCollisionQueryParams TraceParams(FName(TEXT("LineTraceMultiByChannel")), true, nullptr);
    TraceParams.bTraceComplex = false; // Учитывать детализированную коллизию
    TraceParams.bReturnPhysicalMaterial = false; // Возвращать ли материалы коллизии

    TArray<FHitResult> OutHits;

    // Массив каналов коллизии, которые нужно проверить
    TArray<TEnumAsByte<EObjectTypeQuery>> ObjectTypesToTrace;
    ObjectTypesToTrace.Add(UEngineTypes::ConvertToObjectType(ECC_GameTraceChannel1));
    ObjectTypesToTrace.Add(UEngineTypes::ConvertToObjectType(ECC_GameTraceChannel2));
    // Добавьте нужные вам каналы коллизии

    // Выполняем трассировку луча
    bool bHit = GetWorld()->LineTraceMultiByObjectType(
        OutHits,
        StartLocation,
        EndLocation,
        FCollisionObjectQueryParams(ObjectTypesToTrace),
        TraceParams
    );


    if (bHit) {
        for (const FHitResult& hit : OutHits) {
           
            
            if (Cast<AStaticMeshActor>(hit.GetActor()) != nullptr)
                return FTileGraphPositionPair();
            if (Cast<ACPP_GridVisual>(hit.GetActor()) != nullptr) {
                ACPP_Grid* grid = Cast<ACPP_GridVisual>(hit.GetActor())->GetParentGrid();
                
                return FTileGraphPositionPair(UCPP_Utility::GetTileByLocationOnGrid(grid, hit.Location),grid);
            }
                
        }
    }
    return FTileGraphPositionPair();

}

TMap<FIntPoint, FTileData> ACPP_Grid::GetGridTiles()
{
    return gridTiles;
}

void ACPP_Grid::LogTilesPostion()
{
    if(debug)
        for (const auto& item : gridTiles) {
            FVector pos = item.Value.transform.GetLocation();
        
            // Вывод значения FIntPoint
            UE_LOG(LogTemp, Log, TEXT("MyIntPoint: X = %d, Y = %d"), item.Key.X, item.Key.Y);

            // Вывод значения FVector
            UE_LOG(LogTemp, Log, TEXT("MyVector: X = %f, Y = %f, Z = %f"), pos.X, pos.Y, pos.Z);
        }
}

TileType ACPP_Grid::GroundTracing(FVector location, FIntPoint index)
{   
    TileType type = TileType::None;
    FMultiTraceRespond respond = UCPP_Utility::SweepMultiSphereByChannel(GetWorld(), location+FVector(0.f,0.f,-5.f), location + FVector(0.f, 0.f, 5.f),
        tileSize.X/4, ECollisionChannel::ECC_GameTraceChannel1);

    if(!respond.isHit)
        return type;


    type = TileType::Default;

    

    return type;

}

void ACPP_Grid::ModifierTracing(FVector location, FIntPoint index) {
    TileType type = TileType::None;
    FMultiTraceRespond respond = UCPP_Utility::SweepMultiSphereByChannel(GetWorld(), location + FVector(0.f, 0.f, -5.f), location + FVector(0.f, 0.f, 5.f),
        tileSize.X / 4, ECollisionChannel::ECC_GameTraceChannel1);

    
    for (auto& Hit : respond.HitsResult) {
        ACPP_GridModifier* gridMod;

        if ((gridMod = Cast<ACPP_GridModifier>(Hit.GetActor())) != nullptr)
            gridMod->ModifyTile(index, this);
    }


}

void ACPP_Grid::SetTileType(FIntPoint index, TileType type)
{

    if(gridTiles.Find(index))
        gridTiles.Find(index)->type = type;

    GetGridVisualCA()->UpdateTileVisual(gridTiles.FindRef(index));
    
}

void ACPP_Grid::AddLeadTo(FIntPoint index, FTileGraphPositionPair toTile)
{   
    if (gridTiles.Find(index) && toTile.grid != nullptr)
        gridTiles.Find(index)->leadTo.Add(toTile);
    GetGridVisualCA()->UpdateTileVisual(gridTiles.FindRef(index));
}

void ACPP_Grid::AddUnableMoveTo(FIntPoint index, TileDirection direction)
{
    if (gridTiles.Find(index))
        gridTiles.Find(index)->unableMoveTo.AddUnique(direction);
    GetGridVisualCA()->UpdateTileVisual(gridTiles.FindRef(index));
}

void ACPP_Grid::TraceForGridBelow()
{
    FIntPoint prevTile = FIntPoint(-1,-1);
    FIntPoint currentTile = FIntPoint(-1, -1);

    for (int32 X = 0; X < gridSize.X; ++X)
    {
        for (int32 Y = 0; Y < gridSize.Y; ++Y)
        {
            currentTile = FIntPoint(X, Y);

            if (prevTile != FIntPoint(-1, -1) && gridTiles.Contains(currentTile) && gridTiles.Contains(prevTile)) {
                if (gridTiles.Find(currentTile)->type == TileType::None && gridTiles.Find(prevTile)->type != TileType::None) {
                    FTileGraphPositionPair tracedTile = TraceForTileBelow(currentTile, 400);
                    UE_LOG(LogTemp, Log, TEXT("///////////////////%d %d"), tracedTile.index.X, tracedTile.index.Y);
                    if (tracedTile.grid != nullptr)
                        if (UCPP_Utility::IsTileWalkable(tracedTile.grid->GetGridTiles().FindRef(tracedTile.index)))
                            gridTiles.Find(prevTile)->leadTo.Add(tracedTile);
                            
                }

            }
            prevTile = currentTile;
        }
    }

    prevTile = FIntPoint(-1, -1);
    currentTile = FIntPoint(-1, -1);

    for (int32 X = gridSize.X; X > 0; --X)
    {
        for (int32 Y = 0; Y < gridSize.Y; ++Y)
        {
            currentTile = FIntPoint(X, Y);

            if (prevTile != FIntPoint(-1, -1) && gridTiles.Contains(currentTile) && gridTiles.Contains(prevTile)) {
                if (gridTiles.Find(currentTile)->type == TileType::None && gridTiles.Find(prevTile)->type != TileType::None) {
                    FTileGraphPositionPair tracedTile = TraceForTileBelow(currentTile, 400);
                    if (tracedTile.grid != nullptr)
                        if (UCPP_Utility::IsTileWalkable(gridTiles.FindRef(tracedTile.index)))
                            gridTiles.Find(prevTile)->leadTo.Add(tracedTile);

                }

            }
            prevTile = currentTile;
        }
    }

    prevTile = FIntPoint(-1, -1);
    currentTile = FIntPoint(-1, -1);

    for (int32 X = 0; X < gridSize.X; ++X)
    {
        for (int32 Y = gridSize.Y; Y > 0 ; --Y)
        {
            currentTile = FIntPoint(X, Y);

            if (prevTile != FIntPoint(-1, -1) && gridTiles.Contains(currentTile) && gridTiles.Contains(prevTile)) {
                if (gridTiles.Find(currentTile)->type == TileType::None && gridTiles.Find(prevTile)->type != TileType::None) {
                    FTileGraphPositionPair tracedTile = TraceForTileBelow(currentTile, 400);
                    if (tracedTile.grid != nullptr)
                        if (UCPP_Utility::IsTileWalkable(gridTiles.FindRef(tracedTile.index)))
                            gridTiles.Find(prevTile)->leadTo.Add(tracedTile);

                }

            }
            prevTile = currentTile;
        }
    }

    prevTile = FIntPoint(-1, -1);
    currentTile = FIntPoint(-1, -1);

    for (int32 X = gridSize.X; X > 0; --X)
    {
        for (int32 Y = gridSize.Y; Y > 0; --Y)
        {
            currentTile = FIntPoint(X, Y);

            if (prevTile != FIntPoint(-1, -1) && gridTiles.Contains(currentTile) && gridTiles.Contains(prevTile)) {
                if (gridTiles.Find(currentTile)->type == TileType::None && gridTiles.Find(prevTile)->type != TileType::None) {
                    FTileGraphPositionPair tracedTile = TraceForTileBelow(currentTile, 400);
                    if (tracedTile.grid != nullptr)
                        if (UCPP_Utility::IsTileWalkable(gridTiles.FindRef(tracedTile.index)))
                            gridTiles.Find(prevTile)->leadTo.Add(tracedTile);

                }

            }
            prevTile = currentTile;
        }
    }

}


FVector ACPP_Grid::FindCenterLocation()
{
    FVector actorPosition = GetActorTransform().GetLocation();
    return UCPP_Utility::SnapPositionToGrid(actorPosition, tileSize);
}

FVector ACPP_Grid::FindBottomLeftCornerLocation()
{
    FIntPoint gridTileCount = gridSize;
   
    gridTileCount.X = gridTileCount.X - (UCPP_Utility::IsEven(gridTileCount.X) ? 0 : 1);
    gridTileCount.Y = gridTileCount.Y - (UCPP_Utility::IsEven(gridTileCount.Y) ? 0 : 1);

    FVector offset = { 0.0f,0.0f,0.0f };
    offset.X = gridTileCount.X / 2 * tileSize.X;
    offset.Y = gridTileCount.Y / 2 * tileSize.Y;

   
    return gridCenterLocation - offset;
}

void ACPP_Grid::AddGridTile(FTileData data)
{
    gridTiles.Add(data.index, data);
    GetGridVisualCA()->UpdateTileVisual(data);
    
}


