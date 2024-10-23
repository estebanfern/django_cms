
const SUSCRIPTION_BTN = {
    suscribed : {
      btnClass : `btn btn-sm btn-light unsuscribe-btn`,
      btnChildren : `<i class="bi bi-heart-fill"></i> Suscrito`
    },
    unsuscribed : {
      btnClass : `btn btn-sm btn-light suscribe-btn`,
      btnChildren : `<i class="bi bi-heart"></i> Suscribirse`
    }
  }

  $(document).on('click', '.suscribe-btn', function() {
    btn = $(this);
    var category_id = parseInt(btn.attr('category-id'));

    $.ajax({
      url: `/category/${category_id}/suscribe/`,
      type: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function(response) {
        if (response.status === 'success') {
          if (response.checkout_url) {
            window.location.href = response.checkout_url;
          }
          modal.info({message: response.message});
          btn.attr('class', SUSCRIPTION_BTN.suscribed.btnClass);
          btn.html(SUSCRIPTION_BTN.suscribed.btnChildren);
        } else {
          console.error("Error en la respuesta del servidor: " + response.message);
        }
      },
      error: function(xhr, status, error) {
        if (xhr.status === 403) {
          modal.warning({
            message: xhr.responseJSON.message,
          });
        }
        console.error("Error en la solicitud AJAX:", error);
        console.log(xhr);
      }
    });
  });

  $(document).on('click', '.unsuscribe-btn', function() {
    btn = $(this);
    var category_id = parseInt(btn.attr('category-id'));

    $.ajax({
      url: `/category/${category_id}/unsuscribe/`,
      type: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function(response) {
        if (response.status === 'success') {
          modal.info({message: response.message});
          btn.attr('class', SUSCRIPTION_BTN.unsuscribed.btnClass);
          btn.html(SUSCRIPTION_BTN.unsuscribed.btnChildren);
        } else {
          console.error("Error en la respuesta del servidor: " + response.message);
        }
      },
      error: function(xhr, status, error) {
        if (xhr.status === 403) {
          modal.warning({
            message: xhr.responseJSON.message,
          });
        }
        console.error("Error en la solicitud AJAX:", error);
        console.log(xhr);
      }
    });
  });

  $(document).ready(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const successPayment = urlParams.get('stripe_id');
    if (successPayment) {
      modal.info({message: 'Suscripción realizada con éxito!'});
    }
  });
