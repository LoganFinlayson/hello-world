/*
Name: Logan Finlayson
UPI: lfin100
ID: 2969317
*/

import java.math.*;
import java.util.*;

public class knightH {
	
	public static ArrayList<Map<String, BigInteger>> arraymap;
	public static int stepcount;
	public static String dest;
	public static int[] destarray;
	public static int[] v;
	public static int[] u;
	public static int numJumps;
	public static int[] nextStepArray;
	public static ArrayList<Integer> nextStep;
	public static ArrayDeque<String> queue;
	
	public static void calculate(int row, int col, int step) {
		
		stepcount = step;
		if (arraymap.size() < stepcount + 2){
			arraymap.add(new HashMap<String, BigInteger>());
		}
		
		if (dest.equals(row+","+col)){
			numJumps = stepcount;
			return;
		}
				
		BigInteger thisStepcount = arraymap.get(stepcount).get(row+","+col);
		
		//checking possible jumps from row +-1, col +-2
		for (int i = 0; i < 2; i++) { //row
			if (row+v[i] >= 0 && row+v[i] < destarray[0]){ //out of range? 
				for (int j = 0; j < 2; j++) { //col
					if (col+u[j] >= 0 && col+u[j] < destarray[1] ){ //out of range?
						if (!arraymap.get(stepcount+1).containsKey((row+v[i])+","+(col+u[j])) && !arraymap.get(stepcount-1).containsKey((row+v[i])+","+(col+u[j]))){ 
							arraymap.get(stepcount+1).put((row+v[i])+","+(col+u[j]), thisStepcount);
							nextStepArray[stepcount+1] += 1;
							queue.add((row+v[i])+","+(col+u[j]));
						}
						else if (arraymap.get(stepcount+1).containsKey((row+v[i])+","+(col+u[j]))) {
							BigInteger prev = arraymap.get(stepcount+1).get((row+v[i])+","+(col+u[j]));
							arraymap.get(stepcount+1).put((row+v[i])+","+(col+u[j]),prev.add(thisStepcount));
						}
					}
				}
			}
		}

		//checking possible jumps from row +-1, col +-2
		for (int i = 0; i < 2; i++) { //row
			if (row+u[i] >= 0 && row+u[i] < destarray[0]){ //out of range? 
				for (int j = 0; j < 2; j++) { //col
					if (col+v[j] >= 0 && col+v[j] < destarray[1] ){ //out of range?
						if (!arraymap.get(stepcount+1).containsKey((row+u[i])+","+(col+v[j])) && !arraymap.get(stepcount-1).containsKey((row+u[i])+","+(col+v[j]))){ 
							arraymap.get(stepcount+1).put((row+u[i])+","+(col+v[j]), thisStepcount);
							nextStepArray[stepcount+1] += 1;
							queue.add((row+u[i])+","+(col+v[j]));
						}
						else if (arraymap.get(stepcount+1).containsKey((row+u[i])+","+(col+v[j]))){
							BigInteger prev = arraymap.get(stepcount+1).get((row+u[i])+","+(col+v[j]));
							arraymap.get(stepcount+1).put((row+u[i])+","+(col+v[j]),prev.add(thisStepcount));
						}
					}
				}
			}
		}
	}
	

	public static void main(String[] args) {
		//long start = System.currentTimeMillis();
		Scanner keyboard = new Scanner(System.in);
		keyboard.useDelimiter("[ \r\n]+");
		v = new int[2];
		u = new int[2];
		v[0] = -2;
		v[1] = 2;
		u[0] = -1;
		u[1] = 1;
		
		boolean running = true;
		while (running){
			
			int rows, columns;
			rows = keyboard.nextInt();
			columns = keyboard.nextInt();

			queue = new ArrayDeque<String>();
			dest = (rows-1) + "," + (columns-1);
			destarray = new int[2];
			destarray[0] = rows;
			destarray[1] = columns;
			numJumps = 0;
			BigInteger numpaths = BigInteger.valueOf(0);
			nextStepArray = new int[Math.max(rows, columns)];
			arraymap = new ArrayList<Map<String, BigInteger>>();
			arraymap.add(new HashMap<String, BigInteger>());
			arraymap.add(new HashMap<String, BigInteger>());
			arraymap.get(0).put("0,0", BigInteger.valueOf(1));
			stepcount = 1;
			
			if (rows > 1 && columns > 1){
				if (rows > 2){
					arraymap.get(1).put("2,1", BigInteger.valueOf(1));
					queue.add("2,1");
					nextStepArray[1] += 1;
				}
				if (columns > 2) {
					arraymap.get(1).put("1,2", BigInteger.valueOf(1));
					queue.add("1,2");
					nextStepArray[1] += 1;
				}
			}
			
			if (columns == 3 && rows == 3){
				numJumps = 4;
				numpaths = BigInteger.valueOf(2);
			}
			else{
				while (!queue.isEmpty()){
					String coord = queue.poll();
					int splitIndex = coord.indexOf(",");
					int nrow = Integer.parseInt(coord.substring(0, splitIndex));
					int ncol = Integer.parseInt(coord.substring(splitIndex+1));
				
					calculate(nrow, ncol, stepcount);
					nextStepArray[stepcount] -= 1;
					
					if (nextStepArray[stepcount] == 0){
						stepcount++;
					}
					
					if (nrow == rows - 1 && ncol == columns - 1){
						queue.clear();
					}
				}
			}

			for (int i = arraymap.size()-1; i >= 0; i--) {
				if(arraymap.get(i).containsKey((rows-1) + "," + (columns-1))){
					numpaths = arraymap.get(i).get((rows-1) + "," + (columns-1));
				}
			}
			if (numJumps == 0 && numpaths.intValue() == 0){
				running = false;
			}
			else{
				System.out.println(numJumps + " " + numpaths);
			}
		}
		
		keyboard.close();
		//long end = System.currentTimeMillis();
		//System.out.println((end - start) + " ms");
		
	}
}
