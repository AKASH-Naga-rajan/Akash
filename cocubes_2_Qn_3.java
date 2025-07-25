import java.util.Scanner;

public class TargetSumIndices {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter number of elements: ");
        int n = sc.nextInt();
        int[] arr = new int[n];
        System.out.print("Enter array elements: ");
        for(int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        System.out.println("Enter target value: ");
        int target = sc.nextInt();
        boolean found = false;
        for(int i = 0; i < n; i++) {
            for(int j = i+1; j < n; j++) {
                if(arr[i] + arr[j] == target) {
                    System.out.println("Target found at indices " + i + " and " + j);
                    System.out.println("Sum : " + (i + j));
                    found = true;
                    break; 
                }
            }
            if(found)
              break;
        }
        if(!found) {
            System.out.println("No such pair found.");
        }
        sc.close();
    }
}
