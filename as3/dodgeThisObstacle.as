package 
{

	import flash.display.*;
	import flash.events.*;
	import flash.system.*;
	import flash.media.Sound;

	public class Obstacle extends MovieClip
	{

		var stageRef:Stage;
		var speed:Number = 50;
		var obstacleSpawn;
		var dodgeType:int;
		var gameType:String;
		var dodgeObject:Boolean;
		var settings:String;
		var wiggleSize:int;

		public function Obstacle(stageRef:Stage, dodgeType, dodgeObject, gameType, settings):void
		{//add gameType in future

			//initialize speed and position variables
			var xSpeed;
			var ySpeed;
			var rSpeed:int;
			var newSpot:int;
			var diagonalSpeed:int;
			var forwardSpeed:int;
			var rotationSpeed:int;
			var size:int = (1 + int(settings.charAt(1))) * 10;
			var hitSpot:int = size / 5;
			var possibleDirections:int = int(settings.charAt(2));
			var travel:int = int(settings.charAt(3));
			var movement:int = int(settings.charAt(4));
			var death:int = int(settings.charAt(5));
			var sound:int = int(settings.charAt(6));
			var pointValue:int = int(settings.charAt(7));
			//var gravity = 0;
			var wildMovement:Boolean = false;
			var dying:Boolean = false;
			var points:int;//points to add per contact
			var dieSound:Sound;

			//wiggle vars
			var wiggleX:int = 0;
			var wiggleY:int = 0;
			var startX:int = 0;
			var startY:int = 0;

			var loadedImage = this.addChild(new LoadImage(dodgeType,"triangle.png",size,true));
			addEventListener(Event.ENTER_FRAME, events);

			setPoints();

			//for each frame
			function events(evt:Event):void
			{

				//menu state - delete everything for new object
				if (Globals.gameState >= 10)
				{
					removeEventListener(Event.ENTER_FRAME, events);
					evt.target.parent.removeChild(evt.target);
				}
				else if (Globals.gameState == 2 || Globals.gameState >= 4)
				{//title state and ending states - hide object, but keep so reload is not needed on replay
					x = -500;
					y = -500;
				}

				//game state
				if (Globals.gameState == 3)
				{

					//if exiting stage area
					if (x > 700 || x < -100 || y > 500 || y < -100)
					{
						obstacleSpawn = Math.random() * Globals.oddsIncrease * Globals.gameSpeed;
						if (obstacleSpawn > 15)
						{
							spawn();
						}
						else
						{
							Globals.oddsIncrease++;
						}
					}

					hitCheck();

					//after spawn
					if ((newSpot == 0) && (x <= 700) && (x >= -100) && (y <= 500) && (y >= -100))
					{
						x +=  xSpeed;
						y +=  ySpeed;
						//+ gravity;
						//gravity *= 1 - ySpeed * 0.002; trace(ySpeed);
						//rotation += rSpeed;
					}

					switch (movement)
					{//how obstacles move in place
						case 1 :
							wiggle(1);
							break;
						case 2 :
							wiggle(2);
							break;
						case 3 :
							rotation +=  3;
							break;
						case 4 :
							rotation -=  3;
							break;
					}

					if (dying == true)
					{//dying effect
						destroyed();
					}

				}
			}

			function spawn():void
			{//spawning at a new point

				switch (possibleDirections)
				{//where to spawn from
					case 0 :
						newSpot = Math.floor(Math.random() * 4) + 1;//all directions
						break;
					case 1 :
						newSpot = Math.floor(Math.random() * 2) + 1;//left and right
						break;
					case 2 :
						newSpot = Math.floor(Math.random() * 2) + 3;//top and bottom
						break;
					case 3 :
						newSpot = 1;//left
						break;
					case 4 :
						newSpot = 2;//right
						break;
					case 5 :
						newSpot = 3;//top
						break;
					case 6 :
						newSpot = 4;//bottom
						break;
					default :
						newSpot = Math.floor(Math.random() * 4) + 1;//all directions
				}

				obstacleSpawn = 0;
				Globals.oddsIncrease = 0;
				this.visible = true;

				//rotationSpeed = 3 + (1 * Globals.gameSpeed);

				switch (travel)
				{//how obstacles move across screen
					case 0 :
						forwardSpeed = 13.5 * Globals.gameSpeed;//all obstacles at same speed
						diagonalSpeed = 0;
						break;
					case 1 :
						forwardSpeed = (Math.floor(Math.random() * 9) + 9) * Globals.gameSpeed;
						diagonalSpeed = ((Math.floor(Math.random() * 9)) - (Math.floor(Math.random() * 9))) * Globals.gameSpeed;
						break;
					case 2 :
						//wildMovement = true;
						forwardSpeed = 13.5 * Globals.gameSpeed;//all obstacles at same speed
						diagonalSpeed = 0;
						//gravity = 1;
						break;
				}

				switch (newSpot)
				{//spawn result determines new spawn point
					case 1 ://spawn on left
						x = -50;
						y = Math.floor(Math.random() * 400);
						ySpeed = diagonalSpeed;
						xSpeed = forwardSpeed;
						break;
					case 2 ://spawn on right
						x = 650;
						y = Math.floor(Math.random() * 400);
						ySpeed = diagonalSpeed;
						xSpeed =  -  forwardSpeed;
						break;
					case 3 ://spawn on top
						y = -50;
						x = Math.floor(Math.random() * 600);
						xSpeed = diagonalSpeed;
						ySpeed = forwardSpeed;
						break;
					case 4 ://spawn on bottom
						y = 450;
						x = Math.floor(Math.random() * 600);
						xSpeed = diagonalSpeed;
						ySpeed =  -  forwardSpeed;
						break;
				}

				newSpot = 0;

			}


			function wiggle(wiggleSize):void
			{//for wiggle setting
				wiggleX = (Math.floor(Math.random() * 5) - 2) * wiggleSize;//+ or - x
				wiggleY = (Math.floor(Math.random() * 5) - 2) * wiggleSize;//+ or - y
				if (((startX < 10) && (wiggleX < 0)) || ((startX > -10) && (wiggleX > 0)))
				{
					x +=  wiggleX;
					startX +=  wiggleX;
				}
				if (((startY < 10) && (wiggleY < 0)) || ((startY > -10) && (wiggleY > 0)))
				{
					y +=  wiggleY;
					startY +=  wiggleY;
				}
			}

			function setPoints():void
			{//set point values based on saved data

				switch (pointValue)
				{
					case 0 :
						points = 1;
						break;
					case 1 :
						points = 2;
						break;
					case 2 :
						points = 5;
						break;
					case 3 :
						points = 10;
						break;
					case 4 :
						points = 20;
						break;
					case 5 :
						points = 50;
						break;
					case 6 :
						points = 100;
						break;
					case 7 :
						points = 200;
						break;
					case 8 :
						points = 500;
						break;
					case 9 :
						points = 1000;
						break;
				}
			}

			function destroyed():void
			{//when a target gets shot

				switch (death)
				{//how obstacles move during death

					case 0 ://delete
						restartTarget();
						break;

					case 1 ://explode
						addEventListener(Event.ENTER_FRAME, moveToTop);
						loadedImage.width *=  1.5;
						loadedImage.height *=  1.5;
						loadedImage.x -=  loadedImage.x;//+ (loadedImage.width / 2);
						loadedImage.y -=  loadedImage.y;//+ (loadedImage.height / 2);
						if (loadedImage.width >= 9000)
						{
							restartTarget();
						}
						break;

					case 2 ://implode
						loadedImage.width *=  .7;
						loadedImage.height *=  .7;
						if (loadedImage.width <= 1)
						{
							restartTarget();
						}
						break;

					case 3 ://vanish
						loadedImage.image.alpha -=  .1;
						if (loadedImage.image.alpha <= 0)
						{
							restartTarget();
						}
						break;

					case 4 ://fly out
						if ((newSpot == 0) && (x <= 700) && (x >= -100) && (y <= 500) && (y >= -100))
						{
							x -=  xSpeed * 15;
							y -=  ySpeed * 15;
						}
						else
						{
							restartTarget();
						}
						break;
				}
			}

			function moveToTop(evt:Event):void
			{//keep obstacle on top for "explode" death
				MovieClip(root).setChildIndex(MovieClip(evt.target), (MovieClip(root).numChildren - 1));
				removeEventListener(Event.ENTER_FRAME, moveToTop);
			}

			function restartTarget()
			{
				x = -500;
				y = -500;
				loadedImage.width = loadedImage.w;
				loadedImage.height = loadedImage.h;
				loadedImage.image.alpha = 1;
				dying = false;
			}

			function hitCheck():void
			{//if hitting player, game over
				if (hitTestPoint(MovieClip(root).player.x - hitSpot, MovieClip(root).player.y - hitSpot, true)
				|| hitTestPoint(MovieClip(root).player.x - hitSpot, MovieClip(root).player.y + hitSpot, true)
				|| hitTestPoint(MovieClip(root).player.x + hitSpot, MovieClip(root).player.y - hitSpot, true)
				|| hitTestPoint(MovieClip(root).player.x + hitSpot, MovieClip(root).player.y + hitSpot, true)
				|| hitTestPoint(MovieClip(root).player.x, MovieClip(root).player.y, true))
				{
					if (dodgeObject == true)
					{//game over
						Globals.gameState = 4;
					}
					else
					{//collectible
						if (Globals.mute == false)
						{
							switch (sound)
							{//what sound to play on death
								case 0 :
									dieSound = new beepSound();
									break;
								case 1 :
									dieSound = new coin1Sound();
									break;
								case 2 :
									dieSound = new coin2Sound();
									break;
								case 3 :
									dieSound = new coin3Sound();
									break;
								case 4 :
									dieSound = new popSound();
									break;
								case 5 :
									dieSound = new eat1Sound();
									break;
								case 6 :
									dieSound = new eat2Sound();
									break;
								case 7 :
									dieSound = new clickedSound();
									break;
								case 8 :
									dieSound = new gunSound();
									break;
								case 9 :
									dieSound = new deathSound();
									break;
							}
							dieSound.play();
						}
						Globals.score +=  points;
						x = -500;
						y = -500;
						newSpot = 5;//stop moving
					}
				}
			}
		}
	}
}