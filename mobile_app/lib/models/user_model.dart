enum UserRole { user, admin }

class AppUser {
  final String email;
  final UserRole role;

  AppUser({required this.email, required this.role});
}