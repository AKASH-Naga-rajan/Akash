import java.util.Scanner;

public class NotDivisibleByTarget {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // Input start, end, and target
        System.out.print("Enter start number:");
        int start = sc.nextInt();

        System.out.print("Enter end number:");
        int end = sc.nextInt();

        System.out.print("Enter target:");
        int target = sc.nextInt();
          int C=0;
        System.out.println("Numbers not divisible by " + target + " are:");

        for(int i = start; i <= end; i++) {
            if(i % target != 0) {
                    C++;
                System.out.print(i + " ");
            }
        }
         System.out.println(C);
        sc.close();
    }
}
