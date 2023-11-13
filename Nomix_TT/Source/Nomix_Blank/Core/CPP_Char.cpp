// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_Char.h"

// Sets default values
ACPP_Char::ACPP_Char()
{
 	// Set this character to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;
	MovementComponent = GetCharacterMovement();
	

	
	CameraComponent = CreateDefaultSubobject<UCameraComponent>(TEXT("CameraComponent"));
	CameraComponent->SetupAttachment(RootComponent);
	CameraComponent->bUsePawnControlRotation = true;
	

	SkeletalMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("ArmsMeshComponent"));
	SkeletalMeshComponent->SetupAttachment(CameraComponent);

	InventoryComponent = CreateDefaultSubobject<UCPP_InventoryComponent>(TEXT("InventoryComponent"));

	RightHand = CreateDefaultSubobject<UArrowComponent>(TEXT("ArrowComponent"));
	RightHand->SetupAttachment(CameraComponent);
	RightHand->AttachToComponent(SkeletalMeshComponent, FAttachmentTransformRules::KeepRelativeTransform, "R_wrist");

	SphereCollisionComponent = CreateDefaultSubobject<USphereComponent>(TEXT("SphereCollision"));
	SphereCollisionComponent->InitSphereRadius(50.f);
	SphereCollisionComponent->SetupAttachment(RootComponent);
}

// Called when the game starts or when spawned
void ACPP_Char::BeginPlay()
{
	Super::BeginPlay();

	ACPP_GameMode* CurrentGameMode = Cast<ACPP_GameMode>(GetWorld()->GetAuthGameMode());

	if (CurrentGameMode)
		SphereCollisionComponent->SetSphereRadius(CurrentGameMode->interactionRadius);
}

// Called every frame
void ACPP_Char::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

// Called to bind functionality to input
void ACPP_Char::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

}

void ACPP_Char::MoveForward(float value)
{	
	if (freezed)
		return;
	FVector ForwardVector = CameraComponent->GetForwardVector();
	MovementComponent->AddInputVector(ForwardVector * value);
}

void ACPP_Char::MoveRight(float value)
{	
	if (freezed)
		return;
	FVector RightVector = CameraComponent->GetRightVector();
	MovementComponent->AddInputVector(RightVector * value);
}

void ACPP_Char::LookUp(float value)
{	
	if (freezed)
		return;
	AddControllerPitchInput(value);
}

void ACPP_Char::LookRight(float value)
{	
	if (freezed)
	{
		if (objectInAction) {
			ICPP_ItemInteraction* interactionInterface = Cast<ICPP_ItemInteraction>(objectInAction);
			if(interactionInterface)
				interactionInterface->HandleMouseXDrag(this);
		}
	}
	else
		AddControllerYawInput(value);
}

void ACPP_Char::PickUpItem()
{
	ICPP_ItemInteraction* interactionInterface = Cast<ICPP_ItemInteraction>(LookingAtActor());

	
	if (interactionInterface) {
		
		interactionInterface->PickUpItem(this);
	}
}

void ACPP_Char::UseItemStart(AActor* item)
{
	

	if (!item) {
		objectInAction = LookingAtActor();
		item = objectInAction;
	}
	else {
		objectInAction = item;
	}

	if (!item)
		return;

	ICPP_ItemInteraction* interactionInterface = Cast<ICPP_ItemInteraction>(item);

	if (interactionInterface)
		interactionInterface->TriggerItemStart(this);
}

void ACPP_Char::UseItemStop(AActor* item)
{	
	if (!item)
		item = objectInAction;

	if(!item)
		return;

	ICPP_ItemInteraction* interactionInterface = Cast<ICPP_ItemInteraction>(item);

	if (interactionInterface)
		interactionInterface->TriggerItemStop(this);
}

AActor* ACPP_Char::LookingAtActor()
{	

	
	ACPP_GameMode* CurrentGameMode = Cast<ACPP_GameMode>(GetWorld()->GetAuthGameMode());

	if (!CurrentGameMode)
		return nullptr;

	FVector startLocation = CameraComponent->GetComponentLocation();
	FVector endLocation = CameraComponent->GetForwardVector() * CurrentGameMode->interactionRadius + startLocation;

	FCollisionQueryParams TraceParams(FName(TEXT("LineTrace")), true, this);
	TraceParams.bTraceComplex = false;
	TraceParams.AddIgnoredActor(this);

	FHitResult hitResult;

	bool bHit = GetWorld()->LineTraceSingleByChannel(hitResult, startLocation, endLocation, ECC_GameTraceChannel1, TraceParams);
	//DrawDebugLine(GetWorld(), startLocation, endLocation, FColor::Red, false, 5.0f, 0, 1.0f);

	if (bHit)

		return hitResult.GetActor();

	else

		return nullptr;
}

void ACPP_Char::ChooseSlot(int number)
{
	InventoryComponent->SelectSlot(number);
}
