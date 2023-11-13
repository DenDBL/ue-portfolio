// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_PlayerController.h"



void ACPP_PlayerController::SetupInputComponent()
{
	
	Super::SetupInputComponent();
	

	InputComponent->BindAxis("Move Forward/Backward", this, &ACPP_PlayerController::OnMoveForward);
	InputComponent->BindAxis("Move Right/Left", this, &ACPP_PlayerController::OnMoveRight);
	InputComponent->BindAxis("Look Up/Down", this, &ACPP_PlayerController::OnLookUp);
	InputComponent->BindAxis("Look Left/Right", this, &ACPP_PlayerController::OnLookRight);

	InputComponent->BindAction("Pick Up", IE_Pressed, this, &ACPP_PlayerController::PickUpItem);
	InputComponent->BindAction("Trigger", IE_Pressed, this, &ACPP_PlayerController::TriggerItemStart);
	InputComponent->BindAction("Trigger", IE_Released, this, &ACPP_PlayerController::TriggerItemStop);
	InputComponent->BindAction("Choose 1 Slot", IE_Pressed, this, &ACPP_PlayerController::ChooseFirstSlot);
	InputComponent->BindAction("Choose 2 Slot", IE_Pressed, this, &ACPP_PlayerController::ChooseSecondSlot);
}


ACPP_PlayerController::ACPP_PlayerController() {

	

}

void ACPP_PlayerController::BeginPlay()
{
	Super::BeginPlay();

	ControlledCharacter = Cast<ACPP_Char>(GetPawn());
	SetupInputComponent();
}

void ACPP_PlayerController::OnMoveForward(float Value) {

	ControlledCharacter->MoveForward(Value);

}

void ACPP_PlayerController::OnMoveRight(float Value) {

	ControlledCharacter->MoveRight(Value);

}
void ACPP_PlayerController::OnLookUp(float Value) {

	ControlledCharacter->LookUp(Value);

}
void ACPP_PlayerController::OnLookRight(float Value) {

	ControlledCharacter->LookRight(Value);
	axisValueLookRight = Value;

}

void ACPP_PlayerController::PickUpItem() {
	ControlledCharacter->PickUpItem();
}

void ACPP_PlayerController::TriggerItemStart() {
	if (!bIsTriggering)
	{
		bIsTriggering = true;
		ControlledCharacter->UseItemStart();
	}
}

void ACPP_PlayerController::TriggerItemStop() {
	bIsTriggering = false;
	ControlledCharacter->UseItemStop();
}

void ACPP_PlayerController::ChooseFirstSlot()
{
	ControlledCharacter->ChooseSlot(0);
}
void ACPP_PlayerController::ChooseSecondSlot()
{
	ControlledCharacter->ChooseSlot(1);
}