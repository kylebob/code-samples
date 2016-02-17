package 
{

	import flash.display.*;
	import flash.events.*;
	import flash.system.*;
	import flash.media.*;

	public class Collectible extends MovieClip
	{
		var dir:int;
		var gone:Boolean;
		var xStart:int;
		var yStart:int;
		var rStart:int;//rotation
		var xMove:int;
		var yMove:int;

		public function Collectible(xStart, yStart, rStart, xMove, yMove):void
		{

			//initialize speed and position variables
			x = xStart;
			y = yStart;
			rotation = rStart;
			gone = false;

			addEventListener(Event.ENTER_FRAME, events);

			//for each frame
			function events(evt:Event):void
			{

				x +=  xMove;
				y +=  yMove;
				rotation +=  5;

				//if exiting stage area
				if (x > 800 || x < -150 || y > 500 || y < -150 || gone == true)
				{
					removeEventListener(Event.ENTER_FRAME, events);
					evt.target.parent.removeChild(evt.target);
				}
				
			}
		}
	}
}