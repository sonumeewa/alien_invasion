import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep

def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
	#Watch for the keyboard and mouse events.
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event, ai_settings, screen, ship, bullets)

		elif event.type == pygame.KEYUP:
			check_keyup_events(event,ship)

		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)

def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y):
	"""Start a new game when the player clicks Play."""
	"""Start a new game when the player clicks play."""
	button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
	if button_clicked and not stats.game_active:
		#Reset the game settings.
		ai_settings.initialise_dynamic_settings()
		#Hide the mouse cursor.
		pygame.mouse.set_visible(False)

		if play_button.rect.collidepoint(mouse_x, mouse_y):
			#Reset the game statistics.
			stats.reset_stats()
			stats.game_active = True

			#reset the scoreboard images.
			sb.prep_score()
			sb.prep_high_score()
			sb.prep_level()
			sb.prep_ships()

			#Empty the list of aliens and bullets speed up the game.
			aliens.empty()
			bullets.empty()
			ai_settings.increase_speed()

			#Create a new fleet and center the ship.\
			create_fleet(ai_settings, screen, ship, aliens)
			ship.center_ship()

def check_keydown_events(event, ai_settings, screen, ship, bullets):
	"""Respond to keypress."""
	if event.key == pygame.K_RIGHT:
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		ship.moving_left = True
	elif event.key == pygame.K_SPACE:
		fire_bullets(ai_settings, screen, ship, bullets)
	elif event.key == pygame.K_q:
		sys.exit()

def fire_bullets(ai_settings, screen, ship, bullets):
	"""fire bullets if limit is not reached"""

	#Create a new bullet and add it to the bullets group.
	if len(bullets) < ai_settings.bullets_allowed:
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)

def check_keyup_events(event,ship):
	"""Respond to keypress."""
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.key == pygame.K_LEFT:
		ship.moving_left = False


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
	"""update images tp screen and flips the screen"""
	#fill screen with the bg_color
	screen.fill(ai_settings.bg_color)

	#Redraw all bullets behind ship and aliens
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)

	#display the score.
	sb.show_score()

	#Draw the play button if the game is inactive.
	if not stats.game_active:
		play_button.draw_button()

	# Make the most recently drawn screen visible.
	pygame.display.flip()

def update_bullets(ai_settings, screen, stats, sb,ship, aliens, bullets):
	"""Update position the bullets and get rid of the old bullets"""

	#Update bullets position
	bullets.update()

	#Get rid of the bullets that have disappeared.
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
	check_bullet_alien_collision(ai_settings, screen, stats, sb, ship, aliens, bullets)

def check_bullet_alien_collision(ai_settings, screen, stats, sb, ship, aliens, bullets):
	"""Respond to bullet-alien collisions,"""
	#Remove any bullets and aliens that have collided.
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
	
	if len(aliens) == 0:
		#Destroy existing bullets and create a new fleet.
		bullets.empty()
		create_fleet(ai_settings, screen, ship, aliens)

		#if fleet is destroyed increase level
		stats.level +=1
		sb.prep_level()

	if collisions:
		for aliens in collisions.values():
			stats.score += ai_settings.alien_points*len(aliens)
			sb.prep_score()
		check_high_score(stats, sb)

def get_number_alien_x(ai_settings, alien_width):
	"""Determine the number of aliens that fit it a row."""
	available_space_x = ai_settings.screen_width - 2*alien_width
	number_aliens_x = int(available_space_x/(2*alien_width))
	return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height):
	"""Determine the number of rows of aliens that fit on the screen."""
	available_space_y = (ai_settings.screen_height - (5*alien_height) - ship_height)
	number_rows = int(available_space_y/(2*alien_height))
	return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
	"""Create an alien and place it in the row."""
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2*alien_width*alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2*alien.rect.height*row_number
	aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
	"""Create a full fleet of aliens."""
	#Create an alien and find the number of aliens in a row.
	#Spacing between each alien is equal to one alien width.
	alien = Alien(ai_settings, screen)
	number_aliens_x = get_number_alien_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)


	#Create the first row of aliens.
	#Create an alien and place it in the row.
	#Create the flrrt of aliens.
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			create_alien(ai_settings, screen, aliens, alien_number, row_number)


def check_fleet_edges(ai_settings,aliens):
	"""Respond appropriately if any aliens have reached an edge."""
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings,aliens)
			break


def change_fleet_direction(ai_settings,aliens):
	"""Drop the entire fleet and change the fleet's direction"""
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
	"""Respond to ship being hit by aliens"""
	if stats.ship_left >0:
		#Decrement ship_left.
		stats.ship_left -= 1

		#Update ships coreboard
		sb.prep_ships()

		#Empty the list of aliens and bullets.
		aliens.empty()
		bullets.empty()

		#Create a new fleet and center the ship.
		ship.center_ship()

		#Pause.
		sleep(0.5)
	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets):
	"""Check if any aliens have resched the bottom of the screen."""
	
	screen_rect =  screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			#Treat this same as if the ship got hit.
			ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
			break


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
	"""
	check the fleet is at an edge,
	and then update the position of all in the fleet."""

	check_fleet_edges(ai_settings,aliens)
	aliens.update()

	#Look for alien-ship collisions.
	if pygame.sprite.spritecollideany(ship,aliens):
		ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
	#Look for alien hittin the bottom of the ground.
	check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)

def check_high_score(stats, sb):
	"""Check whether there is a high score."""
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score

